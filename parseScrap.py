import json
from enum import Enum
from selenium import webdriver
import helping_function
from bs4 import BeautifulSoup as Bs


class Quality(Enum):
    """
    Enum for item qualities for searching

    First value - BackPack.tf, Regular value
    Second value - Scrap.tf
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


# Creating browser object
options = webdriver.ChromeOptions()
browser = webdriver.Chrome(options=options)

# Waiting for user to log in
browser.get("https://scrap.tf/login")
input()

browser.get("https://scrap.tf/buy/hats")
try:
    as_info = browser.find_element_by_id('category-2')
    products = as_info.find_elements_by_tag_name('div')
except():
    print("Can't find element with id 'category-2'")
    exit(1)
finally:
    pass

html = browser.page_source
html = Bs(html, 'html.parser')
html = html.find('div', attrs={"id": "category-2"}) \
    .find('div', attrs={"class": "items-container"})
items_div = html.find_all('div')
print(items_div)
# bo_price = bo_prices[0].text.strip()

browser.close()
