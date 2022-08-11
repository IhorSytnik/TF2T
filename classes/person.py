import re
from time import sleep

from helping.exceptions import NotLoggedInException
from helping.browser import session
from helping.operations import get_by_xpath_beautifulsoup_full, get_session_id
from settings import TF2_APPID, tf2_PRIMARY_CONTEXTID
from classes.inventory import Inventory


def trying_to_load_inventory_sleep(request_builder, sleep_seconds) -> dict:
    """
    Tries to load inventory with a waiting time between requests.

    :param request_builder: RequestBuilder object.
    :param sleep_seconds: waiting time between each request in seconds.
    :return: steam inventory json (dict).
    """
    while True:
        response = session.request(**request_builder.__dict__)
        inventory_json = response.json()
        if inventory_json['success']:
            break
        sleep(sleep_seconds)
    return inventory_json


class Person:
    def __init__(self, steam_id, custom_url: str = None):
        self.steam_id = steam_id
        self.inventory = Inventory(self.load_inventory())
        self.custom_url = custom_url

    def update_inventory(self):
        return self.inventory.update_inventory(self.load_inventory())

    def load_inventory(self) -> dict:
        request_builder = session.get_request_builder()

        if hasattr(self, 'custom_url'):
            request_builder.url = "".join(
                ["https://steamcommunity.com/id/", self.custom_url, "/inventory/json/", str(TF2_APPID), "/",
                 str(tf2_PRIMARY_CONTEXTID)])
        else:
            request_builder.url = "".join(
                ["https://steamcommunity.com/profiles/", str(self.steam_id), "/inventory/json/", str(TF2_APPID), "/",
                 str(tf2_PRIMARY_CONTEXTID)])

        return trying_to_load_inventory_sleep(request_builder, sleep_seconds=2)

    def get_new_items(self):
        return self.inventory.get_new_items(self.load_inventory()['rgInventory'])


class Partner(Person):
    def __init__(self, trade_partner_id, steam_id, trade_token=None):
        super().__init__(steam_id)
        self.trade_partner_id = trade_partner_id
        self.trade_token = trade_token
        self.trade_inventory = Inventory(self.load_partners_inventory())

    def load_partners_inventory(self) -> dict:
        request_builder = session.get_request_builder()
        request_builder.url = "https://steamcommunity.com/tradeoffer/new/partnerinventory"
        request_builder.params = {
            "sessionid": get_session_id(),
            "partner": self.steam_id,
            "appid": TF2_APPID,
            "contextid": tf2_PRIMARY_CONTEXTID,
        }
        if hasattr(self, 'trade_token'):
            request_builder.headers = {
                'Referer': f'https://steamcommunity.com/tradeoffer/new/?partner={self.trade_partner_id}'
                           f'&token={self.trade_token}'
            }
        else:
            request_builder.headers = {
                'Referer': f'# https://steamcommunity.com/tradeoffer/new/?partner={self.trade_partner_id}'
            }

        return trying_to_load_inventory_sleep(request_builder, sleep_seconds=2)


class Me(Person):
    def __init__(self, steam_id, custom_url: str = None):
        super().__init__(steam_id, custom_url)

    def get_incoming_trades(self) -> list[dict]:
        """

        :return: list of trade dictionaries: {"trade_offer_id": str, "partner_steam_id": str, "partner_trade_id": str}
        """
        request_builder = session.get_request_builder()

        if hasattr(self, 'custom_url'):
            request_builder.url = f'https://steamcommunity.com/id/{self.custom_url}/tradeoffers/'
        else:
            request_builder.url = f'https://steamcommunity.com/id/{self.steam_id}/tradeoffers/'

        response = session.request(**request_builder.__dict__)
        trade_offers = get_by_xpath_beautifulsoup_full(response.text,
                                                       '/html/body/div[1]/div[7]/div[2]/div/div[2]/div[1]') \
            .find_all("div", attrs={"class": "tradeoffer"})
        trades = []
        for offer in trade_offers:
            if offer.find("div", attrs={"class": "tradeoffer_items_banner"}):
                continue
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
    url = response.url
    match = re.search(r"https://steamcommunity.com/login/home/(\s\S)*", url)
    if match is not None:
        raise NotLoggedInException()
    match = re.search(r"https://steamcommunity.com/id/(\w+)/", url)
    if match is None:
        raise Exception("Malformed Response")
    return match.groups()[0]
