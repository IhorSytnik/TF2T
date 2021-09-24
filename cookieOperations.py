import json
from selenium import webdriver


def save_cookie(driver, path):
    """
    Saves a cookie file.

    :param driver: a web driver object that you want to get cookies from
    :param path: path to a cookie file

    Note: Is not used in the program right now.
    """
    with open(path, 'w') as file_handler:
        json.dump(driver.get_cookies(), file_handler)


def load_cookies(driver, path):
    """
    Loads cookies into the web driver.

    :param driver: a web driver object that you want to load cookies into
    :param path: path to a cookie file
    """
    with open(path, 'r') as cookies_file:
        cookies = json.load(cookies_file)
    for cookie in cookies:
        driver.add_cookie(cookie)


if __name__ == '__main__':
    # Creating browser object
    options = webdriver.ChromeOptions()
    browser = webdriver.Chrome(options=options)

    browser.get("https://scrap.tf/login")
    input()
    save_cookie(browser, "cookies/cookiesScrap")

    browser.get("https://backpack.tf/login")
    input()
    save_cookie(browser, "cookies/cookiesBackpack")

    browser.close()
