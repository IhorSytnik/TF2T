import math
from selenium import webdriver
from bs4 import BeautifulSoup as Bs
import cookieOperations as Cop
import parseScrap
import urllib.parse
import re

# Price cap in ref over which this parser can't go
price_capacity = 100000
# Key price in ref
key_price_ref = 59


def parse_backpack(browser, price_cap=price_capacity, key_price=key_price_ref) -> list[dict]:
    """
    Parses Backpack.tf, compares with data from Scrap.tf and then returns sorted dictionary of items that have a
    positive ( and not 0) difference in price

    :param key_price: Key price in ref
    :param price_cap: Price cap in ref over which this parser can't go
    :param browser: WebDriver object
    :return: compared_items - list of sorted by diff item dictionaries that looks like this:
            item = {
                'name': item name with quality,
                'name_base': item name without quality,
                'price_scrap': price in scrap metal on scrap.tf,
                'price_scrap_ref': price in ref on scrap.tf,
                'painted': paint name if painted,
                'quality_name': quality name,
                'quality': quality number,
                'available': quantity of this item available on scrap.tf,
                'price_backpack_keys': price in keys on backpack.tf,
                'price_backpack_ref': price in refs on backpack.tf,
                'diff': price differance between scrap.tf and backpack.tf prices,
                'trade_offer_link': trade offer link of the profitable backpack.tf listing
            }
        Examples:
            item_1 = {
                'name': 'Two Punch Mann',
                'name_base': 'Two Punch Mann',
                'price_scrap': 27,
                'price_scrap_ref': 3.0,
                'painted': '',
                'quality_name': 'Unique',
                'quality': 6,
                'available': '4',
                'price_backpack_keys': 0,
                'price_backpack_refs': '3.11',
                'diff': 0.11,
                'trade_offer_link': 'https://steamcommunity.com/tradeoffer/new/LINKLINKLINK'
            }
    """
    # Loading saved cookies
    browser.get("https://backpack.tf")
    Cop.load_cookies(browser, "cookies/cookiesBackpack")
    compared_items = []

    # For loop for each scrap.tf item that a list from parseScrap.parse_scrap(browser) function has
    for item in parseScrap.parse_scrap(browser):

        # We don't buy/sell items with keys yet
        if float(item['price_scrap_ref']) > price_cap:
            continue

        # Making item name string appropriate for url format
        url = urllib.parse.quote_plus(item['name_base'])

        end_one = False
        count = 0
        page_num = 1
        available = int(item['available'])

        # While loop that works for as many iterations as many of the same items available on scrap.tf
        # Breaks if there is no listings to parse or if the difference in prices is less then one (1) scrap
        # (if price on scrap.tf is more than the price on backpack.tf)
        while count < available:

            if end_one:
                break
            browser.get("https://backpack.tf/classifieds?page=" + str(page_num) + "&item=" + url +
                        "&quality=" + str(item['quality']) + "&tradable=1&craftable=1&australium=-1&killstreak_tier=0")

            item_list = Bs(browser.page_source, 'html.parser') \
                .find('main', attrs={"id": "page-content"}) \
                .find_all('div', attrs={"class": "row"})[1] \
                .find_all('div', attrs={"class": "col-md-6"})[1] \
                .find('ul', attrs={"class": "media-list"}) \
                .find_all('li', attrs={"class": "listing"})

            if not item_list:
                break

            # For loop for each listing
            # Breaks if there are no more available items
            for item_li in item_list:
                if count >= available:
                    break
                item_tag = list(filter(lambda e: e != "\n",
                                       item_li.find_all('i', attrs={"class": "fa-flash"})))
                if item_tag:
                    description = item_li.find('div', attrs={"class": "listing-item"}) \
                        .find('div')
                    if description.has_attr('data-quality_elevated'):
                        continue
                    if description.has_attr('data-paint_name'):
                        if description['data-paint_name'] != item['painted']:
                            continue
                    keys = 0
                    refs = 0
                    price_str = description['data-listing_price']
                    price = re.findall("(\d+\.\d+)|(\d+)", price_str)

                    if len(price) == 2:
                        if not price[0][0] and price[0][1]:
                            keys = price[0][1]
                        elif not price[0][0] and not price[0][1]:
                            pass
                        else:
                            continue
                        if price[1][0] and not price[1][1]:
                            refs = price[1][0]
                        elif not price[1][0] and price[1][1]:
                            refs = price[1][1]
                        elif not price[1][0] and not price[1][1]:
                            pass
                        else:
                            continue
                    elif len(price) == 0:
                        pass
                    elif len(price) == 1:
                        first, *middle, last = price_str.split()
                        if last == "key" or last == "keys":
                            if not price[0][0] and price[0][1]:
                                keys = price[0][1]
                            elif not price[0][0] and not price[0][1]:
                                pass
                            else:
                                continue
                        elif last == "ref":
                            if price[0][0] and not price[0][1]:
                                refs = price[0][0]
                            elif not price[0][0] and price[0][1]:
                                refs = price[0][1]
                            elif not price[0][0] and not price[0][1]:
                                pass
                            else:
                                continue
                    else:
                        continue

                    diff_metal = int(keys) * key_price * 9 + math.trunc(float(refs)) * 9 + \
                        int(math.trunc((float(refs) * 10)) % 10) - float(item['price_scrap'])

                    if diff_metal >= 1:
                        diff_scraps = diff_metal % 9
                        diff_refs = (diff_metal - diff_scraps) / 9

                        item['price_backpack_keys'] = keys
                        item['price_backpack_refs'] = refs
                        item['diff'] = int((diff_refs + (diff_scraps * 11) / 100) * 100) / 100
                        item['trade_offer_link'] = description['data-listing_offers_url']
                        compared_items.append(item)
                        count += 1
                    else:
                        end_one = True
            page_num += 1
    return sorted(compared_items, key=lambda k: k['diff'])


if __name__ == "__main__":
    # Creating browser object
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    try:
        for it in parse_backpack(driver):
            print(it)
    except():
        print("Error")
    finally:
        driver.close()
