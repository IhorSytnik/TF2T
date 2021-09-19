import json

from selenium import webdriver


class BItems:
    def __init__(self):
        self.items = []
        self.b_pos = 0
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
        if self.items[self.b_pos]['mp'] == 'scrap':
            # add here
            self.b_pos += 1
        elif self.items[self.b_pos]['mp'] == 'backpack':
            # add here
            self.b_pos += 1
        else:
            print(self.items[self.b_pos], " Wrong marketplace")
            del self.items[self.b_pos]

    def sell_item(self):
        if self.b_pos >= 0:
            if self.items[0]['mp'] == 'scrap':
                # add here
                del self.items[0]
                self.b_pos -= 1
            elif self.items[0]['mp'] == 'backpack':
                # add here
                del self.items[0]
                self.b_pos -= 1
            else:
                print(self.items[0], " Wrong marketplace")
                del self.items[0]
        else:
            print('Empty buy_list')

if __name__ == '__main__':
    item_list = BItems()
