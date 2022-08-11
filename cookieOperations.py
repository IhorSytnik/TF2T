import json
import os

from selenium import webdriver

from helping.browser import BrowserGET
from helping.controlling import run_once
from settings import BP_URL


def save_cookie(driver, path):
    """
    Saves a cookie file.

    :param driver: a web driver object that you want to get cookies from
    :param path: path to a cookie file

    Note: Is not used in the program right now.
    """
    with open(path, 'w') as file_handler:
        json.dump(driver.get_cookies(), file_handler)


def load_cookies(driver: BrowserGET, path):
    """
    Loads cookies into the web driver.

    :param driver: a web driver object that you want to load cookies into
    :param path: path to a cookie file
    """
    with open(path, 'r') as cookies_file:
        cookies = json.load(cookies_file)
    driver.load_cookies(cookies)


def log_into_steam():
    browser.get("https://steamcommunity.com/")
    input()
    save_cookie(browser, "cookies/cookiesSteam")


def log_into_bp():
    browser.get("https://backpack.tf/login") #  "https://backpacktf.trade/login" When backpack.tf is down they relocate to backpacktf.trade
    input()
    save_cookie(browser, "cookies/cookiesBackpack")


def log_into_scrap():
    browser.get("https://scrap.tf/login")
    input()
    save_cookie(browser, "cookies/cookiesScrap")


@run_once
def load_scraptf_cookies(driver: BrowserGET):
    """
    Loading saved cookies for scrap.tf.

    :param driver: BrowserGET object.
    """
    # browser.get("https://scrap.tf")
    load_cookies(driver, "cookies/cookiesScrap")


@run_once
def load_bptf_cookies(driver: BrowserGET):
    """
    Loading saved cookies for backpack.tf.

    :param driver: BrowserGET object.
    """
    # browser.get(f"https://{BP_URL}")
    load_cookies(driver, "cookies/cookiesBackpack")


@run_once
def load_steam_cookies(driver: BrowserGET):
    """
    Loading saved cookies for backpack.tf.

    :param driver: BrowserGET object.
    """
    # browser.get(f"https://steamcommunity.com")
    load_cookies(driver, "cookies/cookiesSteam")


def load_all_cookies(driver: BrowserGET):
    load_scraptf_cookies(driver)
    load_bptf_cookies(driver)
    load_steam_cookies(driver)


if __name__ == '__main__':
    # Creating browser object
    options = webdriver.ChromeOptions()
    browser = webdriver.Chrome(options=options)

    if not os.path.exists("cookies"):
        os.mkdir("cookies")

    log_into_steam()
    log_into_bp()
    log_into_scrap()

    browser.close()

