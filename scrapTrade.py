import json
import re
from time import sleep

from bs4 import BeautifulSoup as Bs
from requests import Response

import classes.person
import parseScrap
from classes.item import Item
from classes.requestMethod import RequestMethod
from classes.trade import Trade
from cookieOperations import load_steam_cookies
from helping.browser import session
from helping.exceptions import NotEnoughMetalException, OutdatedDataException

load_steam_cookies(session)
sleep_amount = 1.6


def make_form(csrf_token: str, itemswant: list, bot_id: int):
    form = {  # y
        'itemswant': '[' + ','.join(itemswant) + ']',
        'itemsgiving': '[' + ']',
        'bot': bot_id,
        'csrf': csrf_token
    }
    # return urllib.parse.urlencode(form, True)
    return form


def buy(item_list: list, bot_id: int):
    csrf = Bs(session.get('https://scrap.tf/buy/hats').text, 'html.parser') \
        .find('form', attrs={"id": "logoutForm"}) \
        .find('input', attrs={"name": "csrf"})
    response = session.request(RequestMethod.POST, "https://scrap.tf/ajax/hats/BuyHats",
                               data=make_form(csrf['value'], item_list, bot_id),
                               headers={
                                   'referer': 'https://scrap.tf/buy/hats',
                                   'origin': 'https://scrap.tf',
                                   'dnt': '-1',
                                   'accept': 'application/json, text/javascript, */*; q=0.01',
                                   'accept-encoding': 'utf-8',
                                   'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7,ru;q=0.6,uk;q=0.5',
                                   'content-length': '123',
                                   'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                   'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
                                   'sec-ch-ua-mobile': '?0',
                                   'sec-ch-ua-platform': "Windows",
                                   'sec-fetch-dest': 'empty',
                                   'sec-fetch-mode': 'cors',
                                   'sec-fetch-site': 'same-origin',
                                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
                                   'x-requested-with': 'XMLHttpRequest'
                               }
                               )
    print(response)
    print(response.content)
    return response


def trade_thread(item: Item):
    # threading.Thread(target=trade_item, args=(item,)).start()
    trade_item(item)


def update_item_scrap(item: Item):
    updated_item = next((x for x in parseScrap.parse_scrap(browser=session, category=item.category)
                         if x.def_index == item.def_index and
                         x.painted == item.painted and
                         x.craftable == item.craftable and
                         x.quality == item.quality), None)
    if not updated_item or updated_item.price_scrap <= 0:
        raise OutdatedDataException("Scrap.TF doesn't have this item anymore or its price isn't profitable anymore.")
    item.item_id = updated_item.item_id
    item.price_scrap = updated_item.price_scrap
    item.price_scrap_ref = updated_item.price_scrap_ref
    item.price_scrap_full = updated_item.price_scrap_full
    item.available = updated_item.available
    item.bots = updated_item.bots
    return item


def make_me() -> classes.person.Me:
    steam_id_me = re.findall(r'g_steamID = "(.*)"', session.get('https://steamcommunity.com').text)[0]
    custom_url = classes.person.get_custom_url()
    return classes.person.Me(steam_id_me, custom_url)


def trade_item(item: Item):
    success = False
    keep_going_flag = True
    try:
        item = update_item_scrap(item)
    except OutdatedDataException as e:
        # logging.log(logging.INFO, str(e))
        print(e)
        keep_going_flag = False
    items = [item.item_id]
    for bot in [k for k, v in item.bots.items()]:
        sleep(sleep_amount)
        response_json = json.loads(buy(items, bot).content)
        if response_json["success"]:
            break
        elif response_json["message"] == "This bot is no longer available to trade.":
            continue
        elif response_json["message"] == "All of the items you selected were already bought":
            keep_going_flag = False
            break
        else:
            raise Exception("UNEXPECTED ERROR")
    buy_price = item.price_scrap
    item_def_index = item.def_index
    offers = item.offers
    while keep_going_flag:
        incoming_trades = me.get_incoming_trades()
        sleep(sleep_amount)
        for trade in incoming_trades:
            steam_id_partner = trade["partner_steam_id"]
            partner_id_partner = trade["partner_trade_id"]
            trade_offer_id1 = trade["trade_offer_id"]
            partner = classes.person.Partner(partner_id_partner, steam_id_partner, trade_token=None)
            newTrade = Trade(me, partner)
            det = newTrade.get_transaction_details(trade_offer_id1, parseScrap.key_price_metal)
            res: Response
            if det['me'] == buy_price and det['them'][0]['def_index'] == item_def_index:
                sleep(sleep_amount)
                res = newTrade.accept(trade_offer_id1)
            else:
                continue
            print("Check and confirm an incoming trade")
            new_items = []
            while not new_items:
                while not me.update_inventory():
                    sleep(sleep_amount)
                new_items = me.inventory.get_assetids_by_defindex_filtered(item_def_index)
            for offer in offers[1]:
                steam_id_partner = offer.steam_id
                partner_id_partner = offer.trade_id
                token_new = offer.trade_token
                price_bp = offer.price_backpack_metal
                partner = classes.person.Partner(partner_id_partner, steam_id_partner, trade_token=token_new)
                newTrade = Trade(me, partner)
                try:
                    newTrade.sell(price_bp, [(new_items[0], 1)])
                    print('Check if the trade was sent and confirm it')
                    went_through = ''
                    while went_through != 'y' and went_through != 'n':
                        went_through = input('Did it went through? y/n').lower()
                    if went_through == 'y':
                        success = True
                        break
                except NotEnoughMetalException as e:
                    # logging.log(logging.INFO, str(e))
                    print(e)

            keep_going_flag = False
            break
    print(session.websites)
    return success


me = make_me()
