import math
import re

import bs4


# Conversions and other currency operations
def keys_ref_str_to_metal(key_price_str: str) -> int:
    r = re.findall(r'(\d+)\.', key_price_str)
    if len(r) > 0:
        return int((float(r[0]) * 9) + (float(re.findall(r'\.(\d+)', key_price_str)[0]) / 11))
    else:
        return int(re.findall(r'(\d+)', key_price_str)[0]) * 9


def get_metal_from_scraps_recs_refs(scraps: int, recs: int, refs: int) -> int:
    return refs * 9 + recs * 3 + scraps


def get_metal_to_refs(metal: int) -> float:
    return (metal // 9 * 100 + metal % 9 * 11) / 100


def get_refs_to_metal(refs: float) -> int:
    return math.trunc(refs) * 9 + int(math.trunc((refs * 10)) % 10)


def get_keys_to_metal(key_amount: int, key_price_metal: int) -> int:
    return key_amount * key_price_metal


def scrap_to_ref_rec_scrap(metal: int) -> tuple[int, int, int]:
    """

    :return: tuple: (refined metal, reclaimed metal, scrap metal)
    """
    refs = metal // 9
    scraps_w_recs = metal % 9
    scraps = scraps_w_recs % 3
    recs = scraps_w_recs // 3
    return refs, recs, scraps


# Parsing operations.
def get_by_xpath_beautifulsoup_full(text: str, xpath: str) -> bs4.Tag:
    """
    Searches **text** by **xpath**.
    BeautifulSoup does not have the tools to find elements by their xpath
    so this function was made.

    :param text: a code to search in.
    :param xpath: an xpath to search by.
    :return: bs4.Tag object.
    """
    search = bs4.BeautifulSoup(text, 'html.parser')
    list_tag_num = []
    for t in xpath.split('/')[1:]:
        num = re.findall(r"\[(\d+)\]", t)
        name = re.findall(r"(.*)\[", t) if num else re.findall(r"(.*)", t)
        search = search.findChildren(name[0], recursive=False)[int(num[0]) - 1 if num else 0]
        list_tag_num.append({"name": name[0], "num": int(num[0]) if num else 0})
    return search
