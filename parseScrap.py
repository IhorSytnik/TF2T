import math
from enum import Enum
from selenium import webdriver
from bs4 import BeautifulSoup as Bs
import cookieOperations as Cop

# Category to parse on scrap.tf
# 0 - Recently Traded
# 1 - Strange Hats
# 2 - Higher-Value Hats
# 3 - Craft Hats
category_number = 2
# Key selling price in ref (should be set as the buying price on scrap.tf (*Amount we pay them))
key_buy_price_ref = 70.55


class Quality(Enum):
    """
    Enum for item qualities for searching

    First value - BackPack.tf, Regular value
    Second value - Scrap.tf

    Note: is not used for now
    """
    NORMAL = "Normal"
    UNIQUE = "Unique", 6
    VINTAGE = "Vintage", 3
    GENUINE = "Genuine", 1
    STRANGE = "Strange", 11
    UNUSUAL = "Unusual", 5
    HAUNTED = "Haunted", 13
    COLLECTORS = "Collector's"
    DECORATED = "Decorated", 15
    COMMUNITY = "Community"
    SELF_MADE = "Self-Made"
    VALVE = "Valve"


class Paints(Enum):
    """
    Enum for paints

    First value - paint name
    Second value - hex or red team hex for team colours

    Note: is not used for now
    """
    # Single colours
    ZEPHENIAHS_GREED = "Zepheniah's Greed", "#424F3B"
    YE_OLDE_RUSTIC_COLOUR = "Ye Olde Rustic Colour", "#7C6C57"
    THE_COLOR_OF_A_GENTLEMANNS_BUSINESS_PANTS = "The Color of a Gentlemann's Business Pants", "#F0E68C"
    THE_BITTER_TASTE_OF_DEFEAT_AND_LIME = "The Bitter Taste of Defeat and Lime", "#32CD32"
    RADIGAN_CONAGHER_BROWN = "Radigan Conagher Brown", "#694D3A"
    PINK_AS_HELL = "Pink as Hell", "#FF69B4"
    Peculiarly_Drab_Tincture = "Peculiarly Drab Tincture", "#C5AF91"
    PECULIARLY_DRAB_TINCTURE = "Noble Hatter's Violet", "#51384A"
    Muskelmannbraun = "Muskelmannbraun", "#A57545"
    MUSKELMANNBRAUN = "Mann Co. Orange", "#CF7336"
    INDUBITABLY_GREEN = "Indubitably Green", "#729E42"
    DRABLY_OLIVE = "Drably Olive", "#808000"
    DARK_SALMON_INJUSTICE = "Dark Salmon Injustice", "#E9967A"
    COLOR_NO_216_190_216 = "Color No. 216-190-216", "#D8BED8"
    AUSTRALIUM_GOLD = "Australium Gold", "#E7B53B"
    AN_EXTRAORDINARY_ABUNDANCE_OF_TINGE = "An Extraordinary Abundance of Tinge", "#E6E6E6"
    AGED_MOUSTACHE_GREY = "Aged Moustache Grey", "#7E7E7E"
    AFTER_EIGHT = "After Eight", "#2D2D24"
    A_MANNS_MINT = "A Mann's Mint", "#BCDDB3"
    A_DISTINCTIVE_LACK_OF_HUE = "A Distinctive Lack of Hue", "#141414"
    A_DEEP_COMMITMENT_TO_PURPLE = "A Deep Commitment to Purple", "#7D4071"
    A_COLOR_SIMILAR_TO_SLATE = "A Color Similar to Slate", "#2F4F4F"
    # Team colours
    WATER_LOGGED_LAB_COAT = "Waterlogged Lab Coat", "#A89A8C"
    THE_VALUE_OF_TEAMWORK = "The Value of Teamwork", "#803020"
    TEAM_SPIRIT = "Team Spirit", "#B8383B"
    OPERATORS_OVERALLS = "Operator's Overalls", "#483838"
    CREAM_SPIRIT = "Cream Spirit", "#C36C2D"
    BALACLAVAS_ARE_FOREVER = "Balaclavas Are Forever", "#3B1F23"
    AN_AIR_OF_DEBONAIR = "An Air of Debonair", "#654740"


def get_quality(number):
    """
    Requires: quality number, gives: quality name
    Number/Quality correspondence:
        6 = Unique
        3 = Vintage
        1 = Genuine
        11 = Strange
        5 = Unusual
        15 = Decorated

    :param number: quality number
    :return: quality name
    """
    if number == 6:
        return "Unique"
    elif number == 3:
        return "Vintage"
    elif number == 1:
        return "Genuine"
    elif number == 11:
        return "Strange"
    elif number == 5:
        return "Unusual"
    elif number == 15:
        return "Decorated"
    elif number == 13:
        return "Haunted"
    else:
        return


def print_key_price_n_category():
    print(f"parsing category = category-{category_number}")
    print(f"key buying price ref = {key_buy_price_ref:.2f}")


def parse_scrap(browser, category=category_number, key_price=key_buy_price_ref) -> list[dict]:
    """
    Parses Scrap.tf and then returns dictionary of items

    :param key_price: Key selling price in ref (should be set as the buying price on scrap.tf (*Amount we pay them))
    :param category: category to parse on scrap.tf:
        0 - Recently Traded
        1 - Strange Hats
        2 - Higher-Value Hats
        3 - Craft Hats
    :param browser: WebDriver object
    :return: items - list of item dictionaries that looks like this:
            item = {
                'name': item name with quality,
                'name_base': item name without quality,
                'price_scrap': price in scrap metal,
                'price_scrap_ref': price in ref,
                'price_scrap_full': full price in keys and refs,
                'painted': paint name if painted,
                'quality_name': quality name,
                'quality': quality number,
                'available': quantity of this item available
            }
        Examples:
            item_1 = {
                'name': 'Mann of the Seven Sees',
                'name_base': 'Mann of the Seven Sees',
                'price_scrap': 15,
                'price_scrap_ref': 1.66,
                'price_scrap_full': '0 keys, 1.66 refs',
                'painted': 'The Value of Teamwork',
                'quality_name': 'Unique',
                'quality': 6,
                'available': '1'
            }
            item_2 = {
                'name': 'Strange Manndatory Attire',
                'name_base': 'Manndatory Attire',
                'price_scrap': 271,
                'price_scrap_ref': 30.11,
                'price_scrap_full': '0 keys, 30.11 refs',
                'painted': '',
                'quality_name': 'Strange',
                'quality': 11,
                'available': '3'
            }
    """

    # Loading saved cookies
    browser.get("https://scrap.tf")
    Cop.load_cookies(browser, "cookies/cookiesScrap")
    browser.get("https://scrap.tf/buy/hats")
    # browser.get("https://scrap.tf/buy/items")

    # Getting all item divs from web site
    html = browser.page_source
    html = Bs(html, 'html.parser')
    html = html.find('div', attrs={"id": "category-" + str(category)}) \
        .find('div', attrs={"class": "items-container"})
    items_div = html.contents

    items = []

    # For loop for each item
    # Compiling items into dictionary
    for item in list(filter(lambda e: e != "\n", items_div)):
        data_content = Bs(item['data-content'], 'html.parser')
        brs = data_content.contents
        painted = list(filter(lambda e: str(e).startswith('Painted'), brs))

        name = Bs(item['data-title'], 'html.parser')
        span = name.find_all()

        data_item_group_hash = str(item['data-item-group-hash']).split('-')

        dig_hash = int(data_item_group_hash[3])

        metal = int(data_item_group_hash[1])
        scraps = metal % 9
        refs = (metal - scraps) / 9
        ref_full = int((refs + (scraps * 11) / 100) * 100) / 100

        keys = math.trunc(ref_full / key_price) if ref_full >= key_price else 0
        diff_metal_for_keys = float(metal) - int(keys) * (math.trunc(float(key_price)) * 9 + int(
            math.trunc((float(key_price) * 10)) % 10))
        scraps_full_price = diff_metal_for_keys % 9
        refs_full_price = (diff_metal_for_keys - scraps_full_price) / 9
        ref_full_full_price = int((refs_full_price + (scraps_full_price * 11) / 100) * 100) / 100

        items.append({
            'name':             str(name if len(span) == 0 else span[0].contents[0]),
            'name_base':        str(name if len(span) == 0 else span[0].contents[0].split(' ', 1)[1]),
            'price_scrap':      metal,
            'price_scrap_ref':  ref_full,
            'price_scrap_full': str(keys) + ' keys, ' + str(ref_full_full_price) + ' refs',
            'painted':          str('' if len(painted) == 0 else painted[0].removeprefix('Painted ')),
            'quality_name':     get_quality(dig_hash),
            'quality':          dig_hash,
            'available':        item['data-num-available']
        })
    return items


if __name__ == "__main__":
    print_key_price_n_category()
    # Creating browser object
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    try:
        for thing in parse_scrap(driver):
            print(thing)
    except():
        print("Error")
    finally:
        driver.quit()
