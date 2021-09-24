import json

from selenium import webdriver
from bs4 import BeautifulSoup as Bs

from parseScrap import _load_cookies


class BuyItems:
    def __init__(self):
        self.items = []
        options = webdriver.ChromeOptions()
        self.brow = webdriver.Chrome(chrome_options=options)
        self.brow.get("https://scrap.tf")
        _load_cookies(self.brow, "cookies/cookiesScrap")
        self.brow.get("https://scrap.tf/buy/hats")

    def add_item(self, name, price, count, marketplace):
        self.items.append({'name': name,
                           'price': price,
                           'count': count,
                           'painted': marketplace})

    def buy_item(self):
        self.brow.get('https://scrap.tf/buy/hats')
        sequence_number = self.find_item()
        if sequence_number > 0:
            self.send_tradeScrap(sequence_number)
        del self.items[0]

    def send_tradeScrap(self, number):
        self.brow.get('https://scrap.tf/buy/hats')
        self.brow.find_element_by_xpath('//*[@id="category-2"]/div/div[' + str(number) + ']').click()
        self.brow.find_element_by_xpath('//*[@id="trade-btn"]/i').click()
    def find_item(self):
        html = self.brow.page_source
        html = Bs(html, 'html.parser')
        html = html.find('div', attrs={"id": "category-2"}).find('div', attrs={"class": "items-container"})
        items_div = html.contents
        sequence_number = 1
        for item in list(filter(lambda e: e != "\n", items_div)):
            data_content = Bs(item['data-content'], 'html.parser')
            brs = data_content.contents
            painted = list(filter(lambda e: str(e).startswith('Painted'), brs))
            name = Bs(item['data-title'], 'html.parser')
            span = name.find_all()
            if self.items[0]['name'] == str(name if len(span) == 0 else span[0].contents[0]) and \
                    self.items[0]['price'] == item['data-item-value'] and \
                    self.items[0]['painted'] == str('' if len(painted) == 0 else painted[0].removeprefix('Painted ')):
                return sequence_number
            else:
                sequence_number += 1
        return 0


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
    item_list = BuyItems()
    item_list.add_item("Marxman", '15', 1, '')
    item_list.buy_item()
