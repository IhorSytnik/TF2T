import bs4
from bs4 import BeautifulSoup as Bs
import re

import cookieOperations

from classes.item import Item, PriceFull
from helping.browser import BrowserGET, SeleniumChromeWebDriverBrowser, RequestsSessionBrowser
from helping.item_prop import Quality, Paint
from helping.operations import keys_ref_str_to_metal, get_metal_to_refs, get_keys_to_metal
from helping.controlling import run_once
from settings import CATEGORY_NUMBER, PRICE_CAP


driver: BrowserGET
# Key buying price in ref (should be set as the buying price on scrap.tf (*Amount we pay them))
key_price_ref: str
key_price_metal: int
scrap_bot_list = set()


@run_once
def get_key_price(browser: BrowserGET):
    global key_price_ref, key_price_metal
    key_price_ref = get_key_price_from_scrap_tf(browser)
    key_price_metal = keys_ref_str_to_metal(key_price_ref)


def get_key_price_from_scrap_tf(browser: BrowserGET) -> str:
    browser.get("https://scrap.tf")
    cookieOperations.load_cookies(browser, "cookies/cookiesScrap")
    source = browser.go_to_and_get_source_get("https://scrap.tf/keys")
    bs_source = Bs(source, 'html.parser')
    source_html = bs_source.find('div', attrs={"class": "col-md-9 bank-welcome keys-welcome"}) \
        .find_all('h3').copy()[1]
    return str(source_html.find('span').contents[0]).split(' ')[0]


def print_initial_parameters():
    print(f"parsing category = category-{CATEGORY_NUMBER}")
    print(f"key buying price ref = {key_price_ref}")


def get_bots_info(item: bs4.element.Tag) -> dict:
    bots = {}
    for key, value in item.attrs.items():  # iter on both keys and values
        if key.startswith('data-bot'):
            bot_number = re.findall(r'data-bot(\d+)-count', key)[0]
            scrap_bot_list.add(bot_number)
            bots[bot_number] = int(value)
    return bots


def parse_scrap(browser: BrowserGET, category=CATEGORY_NUMBER) -> list[Item]:
    """
    Parses Scrap.tf and then returns dictionary of items

    :param category: category to parse on scrap.tf:
        0 - Recently Traded
        1 - Strange Hats
        2 - Higher-Value Hats
        3 - Craft Hats
    :param browser: BrowserGET object
    :return: items - list of items
    """
    get_key_price(browser)

    # Loading saved cookies
    browser.get("https://scrap.tf")
    cookieOperations.load_cookies(browser, "cookies/cookiesScrap")

    # Getting all item divs from the web site
    html = browser.go_to_and_get_source_get("https://scrap.tf/buy/hats")
    # html = browser.go_to_and_get_source_get("https://scrap.tf/buy/items")
    html = Bs(html, 'html.parser')
    html = html.find('div', attrs={"id": "category-" + str(category)}) \
        .find('div', attrs={"class": "items-container"})
    items_div: list[bs4.element.Tag] = html.contents

    items = []

    # For loop for each item
    # Compiling items into dictionary
    for item in list(filter(lambda e: e != "\n", items_div)):
        data_item_group_hash = str(item['data-item-group-hash']).split('-')
        metal = int(data_item_group_hash[1])

        if metal > PRICE_CAP:
            continue

        painted = re.findall(r"<br/>Painted (.+?)<br/>", item['data-content'])

        name = Bs(item['data-title'], 'html.parser')
        span = name.find_all()

        ref_full = get_metal_to_refs(metal)
        keys = metal // key_price_metal
        refs = get_metal_to_refs(metal - get_keys_to_metal(keys, key_price_metal))

        items.append(Item(
            name=               str(name if len(span) == 0 else span[0].contents[0]),
            name_base=          str(name if len(span) == 0 else span[0].contents[0].split(' ', 1)[1]),
            item_id=            str(item['data-id']),
            price_scrap=        metal,
            price_scrap_ref=    ref_full,
            price_scrap_full=   PriceFull(
                                    keys=keys,
                                    refs=refs
                                ),
            painted=            Paint('' if len(painted) == 0 else painted[0]),
            def_index=          item['data-defindex'],
            quality=            Quality(int(data_item_group_hash[3])),
            craftable=          'uncraft' not in str(item['class']).split(),
            available=          int(item['data-num-available']),
            bots=               get_bots_info(item),
            offers=             list()
        ))
    return items


if __name__ == "__main__":
    driver = RequestsSessionBrowser()
    # driver = SeleniumChromeWebDriverBrowser()

    try:
        for cn in range(1, 4):
            for thing in parse_scrap(driver, cn):
                print(thing)
                # pass
    except():
        print("Error")
    finally:
        driver.quit()

