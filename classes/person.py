import re

from bs4 import BeautifulSoup as Bs

from helping.exceptions import NotLoggedInException
from classes.requestMethod import RequestMethod
from helping.browser import session
from helping.operations import get_by_xpath_beautifulsoup_full
from settings import TF2_APPID, tf2_PRIMARY_CONTEXTID
from classes.inventory import Inventory


class Person:
    def __init__(self, steam_id, custom_url: str = None):
        self.steam_id = steam_id
        self.inventory = Inventory(self.load_inventory())
        self.custom_url = custom_url

    def load_inventory(self) -> dict:
        if hasattr(self, 'custom_url'):
            url = "".join(["https://steamcommunity.com/id/", self.custom_url, "/inventory/json/", str(TF2_APPID), "/",
                           str(tf2_PRIMARY_CONTEXTID)])
        else:
            url = "".join(
                ["https://steamcommunity.com/profiles/", str(self.steam_id), "/inventory/json/", str(TF2_APPID), "/",
                 str(tf2_PRIMARY_CONTEXTID)])
        return session.get(url).json()

    def get_new_items(self):
        return self.inventory.get_new_items(self.load_inventory()['rgInventory'])


class Partner(Person):
    def __init__(self, trade_partner_id, session_id, steam_id, trade_token=None):
        super().__init__(steam_id)
        self.trade_partner_id = trade_partner_id
        self.trade_token = trade_token
        self.session_id = session_id
        # self.trade_inventory: dict = self.load_partners_inventory()
        self.trade_inventory = Inventory(self.load_partners_inventory())

    def load_partners_inventory(self) -> dict:
        trade_inventory_url = "https://steamcommunity.com/tradeoffer/new/partnerinventory"
        parameters = {
            "sessionid": self.session_id,
            "partner": self.steam_id,
            "appid": TF2_APPID,
            "contextid": tf2_PRIMARY_CONTEXTID,
        }
        if hasattr(self, 'trade_token'):
            headers = {
                'Referer': f'https://steamcommunity.com/tradeoffer/new/?partner={self.trade_partner_id}'
                           f'&token={self.trade_token}'
            }
        else:
            headers = {
                'Referer': f'# https://steamcommunity.com/tradeoffer/new/?partner={self.trade_partner_id}'
            }
        return session.request(RequestMethod.GET, trade_inventory_url,
                               params=parameters,
                               headers=headers
                               ).json()


def get_incoming_trades() -> list[dict]:
    response = session.get('https://steamcommunity.com')
    steam_name_id = Bs(response.text, 'html.parser') \
        .find('div', attrs={"class": "responsive_menu_user_persona"}) \
        .findChildren('a')[1].contents[0]
    response1 = session.get(f'https://steamcommunity.com/id/{steam_name_id}/tradeoffers/')
    trade_offers = get_by_xpath_beautifulsoup_full(response1.text,
                                                   '/html/body/div[1]/div[7]/div[2]/div/div[2]/div[1]') \
        .find_all("div", attrs={"class": "tradeoffer"})
    trades = []
    for offer in trade_offers:
        trade_offer_id = re.findall(r"tradeofferid_(\d+)", offer["id"])[0]
        partner_steam_id = re.findall(r"ReportTradeScam\( '(\d+)'",
                                      offer.find("a")["onclick"])[0]
        partner_trade_id = offer.find("div", attrs={"class": "tradeoffer_partner"}).find("div")["data-miniprofile"]
        trades.append({"trade_offer_id": trade_offer_id,
                       "partner_steam_id": partner_steam_id,
                       "partner_trade_id": partner_trade_id})
    return trades


def get_custom_url():
    response = session.get("https://steamcommunity.com/my")
    if response.status_code != 200:
        raise Exception("Malformed response")
    url = response.url
    match = re.search(r"https://steamcommunity.com/login/home/(\s\S)*", url)
    if match is not None:
        raise NotLoggedInException()
    match = re.search(r"https://steamcommunity.com/id/(\w+)/", url)
    if match is None:
        raise Exception("Malformed Response")
    return match.groups()[0]