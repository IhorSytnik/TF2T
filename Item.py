import json
import time
from telnetlib import EC

from bs4 import BeautifulSoup as Bs
from selenium import webdriver
from parseScrap import _load_cookies


class BuyItems:
    def __init__(self):
        self.items = []
        self.purchased_items = []
        options = webdriver.ChromeOptions()
        options.headless()
        self.brow = webdriver.Chrome(chrome_options=options)
        self.brow.get("https://scrap.tf")
        _load_cookies(self.brow, "cookies/cookiesScrap")
        self.brow.get("https://scrap.tf/buy/hats")

    def add_item(self, name="Marxman", price='15', count=1, color=''):
        self.items.append({'name': name,
                           'price': price,
                           'count': count,
                           'painted': color})

    def _add_purchased_item(self, name, count, color):
        self.purchased_items.append({'name': name,
                                     'count': count,
                                     'painted': color})

    def get_purchased_items(self):
        return self.purchased_items

    def buy(self, count_items=1):
        if self.brow.current_url != 'https://scrap.tf/buy/hats':
            self.brow.get('https://scrap.tf/buy/hats')
        item_parameters = self._find_item()
        if int(item_parameters[0]) > 0:
            for i in range(
                    item_parameters[1] if self.items[0]['count'] > item_parameters[1] else self.items[0]['count']):
                self.brow.find_element_by_xpath(
                    '//*[@id="category-2"]/div/div[' + str(item_parameters[0]) + ']').click()
            item_parameters = self._find_item()
            self._add_purchased_item(self.items[0]['name'], item_parameters[2], self.items[0]['painted'])
        del self.items[0]
        if count_items > 1:
            return self.buy(count_items - 1)

        self.brow.find_element_by_xpath('//*[@id="trade-btn"]/i').click()
        time.sleep(30)
        self.brow.find_element_by_xpath('//*[@id="pid-hats"]/div[3]/div/div[2]/div[2]/button[2]').click()
        self.brow.switch_to.window(self.brow.window_handles[1])
        self.brow.find_element_by_xpath('//*[@id="you_notready"]/div/text()').click()
        self.brow.find_element_by_xpath('//*[@id="trade_confirmbtn_text"]').click()
        time.sleep(2)
        self.brow.close()
        self.brow.switch_to.window(self.brow.window_handles[0])

        # TODO add accepting with Steam

    def _find_item(self):
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
                return [sequence_number, int(item['data-num-available']), int(item['data-num-selected'])]
            else:
                sequence_number += 1
        return [0, 0, 0]
    # TODO refactor _find_items (find better way of finding items)


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
    item_list.add_item("Made Man", '15', 1, '')
    item_list.buy()
