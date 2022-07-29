import json
import os

from selenium import webdriver

from helping.browser import BrowserGET


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


def log_in_to_steam():
    browser.get("https://steamcommunity.com/")
    input()
    save_cookie(browser, "cookies/cookiesSteam")


def log_in_to_bp():
    browser.get("https://backpack.tf/login") #  "https://backpacktf.trade/login" When backpack.tf is down they relocate to backpacktf.trade
    input()
    save_cookie(browser, "cookies/cookiesBackpack")


def log_in_to_scrap():
    browser.get("https://scrap.tf/login")
    input()
    save_cookie(browser, "cookies/cookiesScrap")


if __name__ == '__main__':
    # Creating browser object
    options = webdriver.ChromeOptions()
    browser = webdriver.Chrome(options=options)

    if not os.path.exists("cookies"):
        os.mkdir("cookies")

    log_in_to_steam()
    log_in_to_bp()
    log_in_to_scrap()

    browser.close()
