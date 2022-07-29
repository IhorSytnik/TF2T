import sys
from time import sleep

from bs4 import BeautifulSoup as Bs
from bs4.element import ResultSet

import cookieOperations
import parseScrap
import urllib.parse
import re

from classes.item import Offer, Item, PriceFull
from helping.browser import BrowserGET, RequestsSessionBrowser
from helping.exceptions import StatusCodeException
from helping.item_prop import Paint
from helping.operations import keys_ref_str_to_metal, get_metal_to_refs, get_keys_to_metal, get_refs_to_metal
from helping.controlling import run_once
from scrap_trade import trade_thread
from settings import KEY_SELLING_PRICE_REF, SAFE_PILLOW, BLACKLIST

driver: BrowserGET
key_price_metal: int


@run_once
def get_key_price():
    global key_price_metal
    key_price_metal = keys_ref_str_to_metal(KEY_SELLING_PRICE_REF)


def print_initial_parameters():
    print(f"key selling price ref = {KEY_SELLING_PRICE_REF}")


def parse_backpack(browser: BrowserGET, category) -> list[Item]:
    """
    Parses Backpack.tf, compares with data from Scrap.tf and then returns sorted dictionary of items that have a
    positive ( and not 0) difference in price

    :param category:
    :param browser: BrowserGET object
    :return: compared_items - list of sorted by diff items
    """
    get_key_price()

    bp_url = 'backpack.tf'  # they relocate the web-site when their server has issues or something
    print_initial_parameters()
    # Loading saved cookies
    browser.get(f"https://{bp_url}")
    cookieOperations.load_cookies(browser, "cookies/cookiesBackpack")
    compared_items = []

    # For loop for each scrap.tf item that a list from parseScrap.parse_scrap(browser) function has
    for item in parseScrap.parse_scrap(browser, category=category):

        # Making item name string appropriate for url format
        name_base_url = urllib.parse.quote_plus(item.name_base)

        end_flag = False
        count = 0
        page_num = 1
        available = item.available
        available_safe_pillow = available + SAFE_PILLOW
        offers = []

        # While loop that works for as many iterations as many of the same items available on scrap.tf
        # Breaks if there is no listings to parse or if the difference in prices is less then one (1) scrap
        # (if price on scrap.tf is more than the price on backpack.tf)
        while not end_flag and count < available_safe_pillow:

            link = f"https://{bp_url}/classifieds?page={page_num}&item={name_base_url}&" \
                   f"quality={item.quality.get_index()}&tradable=1&craftable={1 if item.craftable else -1}" \
                   f"&australium=-1&killstreak_tier=0&paint={item.painted.get_bp_code()}&offers=1"
            # sys.stdout.write("\r{0}".format(link))
            # sys.stdout.flush()

            while True:
                sleep(0.66)
                try:
                    # Gets all sell offers with the "lightning" button
                    item_list: ResultSet = Bs(browser.get_page_source(), 'html.parser') \
                        .find_all('ul', attrs={"class": "media-list"})[1] \
                        .find_all('i', attrs={"class": "fa-flash"})
                    # item_list: ResultSet = Bs(browser.get_page_source(), 'html.parser') \
                    #     .find('span', text="Buy Orders") \
                    #     .parent.parent \
                    #     .find('ul', attrs={"class": "media-list"}) \
                    #     .find_all('i', attrs={"class": "fa-flash"})
                    if 600 > browser.get_status_code() >= 500:
                        continue
                    elif browser.get_status_code() == 426:
                        sleep(2)
                        continue
                    else:
                        raise StatusCodeException()
                except AttributeError as e:
                    print(browser.get_status_code())
                    continue
                except IndexError as e:
                    print(browser.get_status_code())
                    continue

            if not item_list:
                break

            # For loop for each listing
            # Breaks if there are no more available items
            for item_li in item_list:
                if count >= available_safe_pillow or end_flag:
                    break

                # Gets the parent[4] of the "lightning" button tag and then the item's description
                li_listing = item_li.parent.parent.parent.parent.parent
                description = li_listing.find('div', attrs={"class": "listing-item"}) \
                                        .find('div')

                price_str = description['data-listing_price']
                price_keys = re.findall(r'(\d+) key', price_str)
                price_ref = re.findall(r'(\d+\.\d+|\d+) ref', price_str)
                keys = 0 if not price_keys else int(price_keys[0])
                refs = 0. if not price_ref else float(price_ref[0])
                bp_metal = get_keys_to_metal(keys, key_price_metal) + get_refs_to_metal(refs)
                diff_metal = bp_metal - item.price_scrap
                print(diff_metal)

                if diff_metal <= 0:
                    end_flag = True
                    break

                if description.has_attr('data-quality_elevated') or \
                        description['data-listing_account_id'] in BLACKLIST:
                    continue
                elif description.has_attr('data-paint_name'):
                    continue

                offers.append(Offer(
                    price_backpack=         PriceFull(
                                                keys=keys,
                                                refs=refs
                                            ),
                    price_backpack_metal=   bp_metal,
                    diff_metal=             diff_metal,
                    diff_ref=               get_metal_to_refs(diff_metal),
                    steam_id=               li_listing.find('a', attrs={"class": "user-link"})['data-id'],
                    trade_id=               re.findall(r'partner=(\d+)&', description['data-listing_offers_url'])[0],
                    trade_token=            re.findall(r'token=(.*)', description['data-listing_offers_url'])[0],
                    trade_offer_link=       description['data-listing_offers_url']
                ))
                count += 1
            page_num += 1
        if len(offers) >= 2:
            item.offers = offers
            print(link)
            print(offers[0].diff_metal)
            print(item)
            trade_thread(item)
            compared_items.append(item)
    return sorted(compared_items, key=lambda i: i.offers[0].diff_metal)


if __name__ == "__main__":

    # Creating browser object
    driver = RequestsSessionBrowser()
    # driver = SeleniumChromeWebDriverBrowser()
    cookieOperations.load_cookies(driver, "cookies/cookiesSteam")

    try:
        # for trade_category in range(3, 0, -1):
        for trade_category in range(1, 4):
            for it in parse_backpack(driver, category=trade_category):
                print(it)
                pass
    except():
        print("Error")
    finally:
        driver.quit()
