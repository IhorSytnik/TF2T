import json
from enum import Enum
from selenium import webdriver
from bs4 import BeautifulSoup as Bs


class Quality(Enum):
    """
    Enum for item qualities for searching

    First value - BackPack.tf, Regular value
    Second value - Scrap.tf

    Note: Is not used in the program right now.
    """
    Normal = "Normal"
    Unique = "Unique", "quality6"
    Vintage = "Vintage", "quality3"
    Genuine = "Genuine", "quality1"
    Strange = "Strange", "quality11"
    Unusual = "Unusual", "quality5"
    Haunted = "Haunted"
    Collectors = "Collector's"
    Decorated = "Decorated"
    Community = "Community"
    SelfMade = "Self-Made"
    Valve = "Valve"


def _save_cookie(driver, path):
    """
    Saves a cookie file.

    :param driver: a web driver object that you want to get cookies from
    :param path: path to a cookie file

    Note: Is not used in the program right now.
    """
    with open(path, 'w') as file_handler:
        json.dump(driver.get_cookies(), file_handler)


def _load_cookies(driver, path):
    """
    Loads cookies into the web driver.

    :param driver: a web driver object that you want to load cookies into
    :param path: path to a cookie file
    """
    with open(path, 'r') as cookies_file:
        cookies = json.load(cookies_file)
    for cookie in cookies:
        driver.add_cookie(cookie)


def parse_scrap():
    """
    Parses Scrap.tf and then returns dictionary of items

    :return: items - item dictionary that looks like this:
            item = {
                'name': item name,
                'price': price in scrap metal,
                'painted': paint name if painted,
                'available': quantity of this item available
            }
        Examples:
            item_1 = {
                'name': 'Mann of the Seven Sees',
                'price': '1797',
                'painted': 'The Value of Teamwork',
                'available': '1'
            }
            item_2 = {
                'name': 'Byte'd Beak',
                'price': '627',
                'painted': '',
                'available': '3'
            }
    """
    # Creating browser object
    options = webdriver.ChromeOptions()
    browser = webdriver.Chrome(options=options)

    # Loading saved cookies
    browser.get("https://scrap.tf")
    _load_cookies(browser, "cookiesScrap")
    browser.get("https://scrap.tf/buy/hats")

    # Getting all item divs from web site
    html = browser.page_source
    html = Bs(html, 'html.parser')
    html = html.find('div', attrs={"id": "category-2"}) \
        .find('div', attrs={"class": "items-container"})
    items_div = html.contents

    # Compiling items into dictionary
    items = []
    for item in list(filter(lambda e: e != "\n", items_div)):
        data_content = Bs(item['data-content'], 'html.parser')
        brs = data_content.contents
        painted = list(filter(lambda e: str(e).startswith('Painted'), brs))
        name = Bs(item['data-title'], 'html.parser')
        span = name.find_all()
        items.append({
            'name': str(name if len(span) == 0 else span[0].contents[0]),
            'price': item['data-item-value'],
            'painted': str('' if len(painted) == 0 else painted[0].removeprefix('Painted ')),
            # 'paint_hex': '',
            'available': item['data-num-available']
        })
    browser.close()
    return items
