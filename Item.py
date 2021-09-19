import json

from selenium import webdriver


class BuyItems:
    def __init__(self):
        self.items = []
        options = webdriver.ChromeOptions()
        self.brow = webdriver.Chrome(chrome_options=options)
        self.brow.get("https://steamcommunity.com/")
        file = open("cookies.txt", 'r')
        cookies = json.load(file)
        for cookie in cookies:
            self.brow.add_cookie(cookie)
        file.close()
        self.brow.refresh()

    def add_item(self, name, price, count, marketplace):
        self.items.append({'name': name.replace(" ", "%20"),
                           'price': price,
                           'count': count,
                           'mp': marketplace})

    def buy_item(self):
        if self.items[0]['mp'] == 'scrap':
            # add here
            del self.items[0]
        elif self.items[0]['mp'] == 'backpack':
            # add here
            del self.items[0]
        else:
            print(self.items[0], " Wrong marketplace")
            del self.items[0]


class SellItems:
    def __init__(self):
        self.items = []
        options = webdriver.ChromeOptions()
        self.brow = webdriver.Chrome(chrome_options=options)
        self.brow.get("https://steamcommunity.com/")
        file = open("cookies.txt", 'r')
        cookies = json.load(file)
        for cookie in cookies:
            self.brow.add_cookie(cookie)
        file.close()
        self.brow.refresh()

    def add_item(self, name, price, count, marketplace):
        self.items.append({'name': name.replace(" ", "%20"),
                           'price': price,
                           'count': count,
                           'mp': marketplace})

    def sell_item(self):
        if self.items[0]['mp'] == 'scrap':
            # add here
            del self.items[0]
        elif self.items[0]['mp'] == 'backpack':
            # add here
            del self.items[0]
        else:
            print(self.items[0], " Wrong marketplace")
            del self.items[0]

if __name__ == '__main__':
    item_list = SellItems()
