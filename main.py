from cookieOperations import load_all_cookies
from helping.browser import RequestsSessionBrowser
from parseBackpack import parse_backpack

if __name__ == '__main__':
    driver = RequestsSessionBrowser()
    load_all_cookies(driver)

    try:
        # for trade_category in range(3, 0, -1):
        for trade_category in range(1, 4):
            for it in parse_backpack(driver, category=trade_category):
                # print(it)
                pass
    except():
        print("Error")
    finally:
        driver.quit()
