import json
import re

import requests

from helping.browser import session
from classes.requestMethod import RequestMethod
from helping.exceptions import NotEnoughMetalException
from helping.operations import scrap_to_ref_rec_scrap, get_session_id
from settings import TF2_APPID, tf2_PRIMARY_CONTEXTID
from helping.currencies import Currencies
from classes.person import Partner, Me
from classes.inventory import Inventory


class Trade:
    def __init__(self, me: Me, partner: Partner):
        self.partner = partner
        self.me = me
        # b'{"tradeofferid":str, "needs_mobile_confirmation":boolean, "needs_email_confirmation":boolean,
        # "email_domain":str(ex:"gmail.com")}'
        self.trade_offer_info = None
        self.trade_items = None

    def __compile_items(self, item_list: list[tuple[str, int]]):
        """

        :param item_list: tuple(item asset id, amount)
        :return:
        """
        return [{
            "appid": TF2_APPID,  # always needs to be an int
            "contextid": tf2_PRIMARY_CONTEXTID,  # always needs to be a string
            "amount": item_amount,  # always needs to be an int
            "assetid": item_assetid  # always needs to be a string
        } for item_assetid, item_amount in item_list]

    def __make_offerdata(self, my_item_list: list[tuple], partners_item_list: list[tuple]):
        return {
            "newversion": True,
            "version": 6,  # 2,
            "me": {
                "assets": self.__compile_items(my_item_list),
                "currency": [],
                "ready": False
            },
            "them": {
                "assets": self.__compile_items(partners_item_list),
                "currency": [],
                "ready": False
            },
            # 'captcha': ""
        }

    def __make_form(self, my_item_list: list[tuple], partners_item_list: list[tuple]):
        params = {
            "trade_offer_access_token": self.partner.trade_token,
        }
        form = {  # y
            "sessionid": get_session_id(),
            "serverid": 1,
            "partner": self.partner.steam_id,
            "tradeoffermessage": '',
            "json_tradeoffer": json.dumps(self.__make_offerdata(my_item_list, partners_item_list),
                                          separators=(',', ':')),
            'captcha': "",  #
            "trade_offer_create_params": json.dumps(params, separators=(',', ':')),
            "tradeofferid_countered": ''
        }
        return form

    def send_trade(self, my_item_list: list[tuple],
                   partners_item_list: list[tuple]) -> requests.Response:
        response = session.request(RequestMethod.POST, "https://steamcommunity.com/tradeoffer/new/send",
                                   data=self.__make_form(my_item_list, partners_item_list),
                                   headers={
                                       'Referer': f'https://steamcommunity.com/tradeoffer/new/'
                                                  f'?partner={self.partner.trade_partner_id}'
                                                  f'&token={self.partner.trade_token}'
                                   }
                                   )
        self.trade_offer_info = response.json()
        return response

    def __get_metal(self, refs, recs, scraps, inv) -> list:
        result = []
        for m in inv.scraps[:scraps]:
            result.append((m['id'], 1))
        for m in inv.recs[:recs]:
            result.append((m['id'], 1))
        for m in inv.refs[:refs]:
            result.append((m['id'], 1))
        return result

    def __get_metal_for_trade_enough(self, price, inv: Inventory) -> list:
        if inv.count_currency()['metal'] < price:
            raise Exception("You don't have enough metal for change.")
        item_list = []
        refs, recs, scraps = scrap_to_ref_rec_scrap(price)
        rc_is = len(inv.recs)
        s_is = len(inv.scraps)
        rf_is = len(inv.refs)
        if rf_is >= refs and s_is >= scraps and rc_is >= recs:  # enough
            item_list.extend(self.__get_metal(
                scraps=scraps, recs=recs, refs=refs, inv=inv))
        elif rf_is >= refs and rc_is < recs:  # not enough reclaimed metal
            if s_is >= scraps + recs * 3:
                item_list.extend(self.__get_metal(
                    scraps=scraps + (recs - rc_is) * 3, recs=rc_is, refs=refs, inv=inv))
        elif rf_is < refs:  # not enough refined metal
            dif_ref = (refs - rf_is) * 9
            need_rec = dif_ref // 3
            need_scrap = dif_ref % 3
            if rc_is >= need_rec and s_is >= need_scrap:  # + the rest is enough
                item_list.extend(self.__get_metal(
                    scraps=need_scrap, recs=need_rec, refs=refs, inv=inv))
            elif rc_is < need_rec and s_is >= need_scrap:  # + not enough reclaimed metal
                item_list.extend(self.__get_metal(
                    scraps=need_scrap + (need_rec - rc_is) * 3, recs=need_rec, refs=refs, inv=inv))
        return item_list

    def __get_metal_for_trade(self, refs: int, recs: int, scraps: int, price: int, partner_inv: Inventory,
                              my_inv: Inventory) -> tuple[list, list]:
        partner_item_list = []
        my_item_list = []
        rc_is = len(partner_inv.recs)
        s_is = len(partner_inv.scraps)
        rf_is = len(partner_inv.refs)
        if rf_is < refs:
            dif_ref = (refs - rf_is) * 9
            need_rec = dif_ref // 3
            need_scrap = dif_ref % 3
        if rf_is >= refs and rc_is < recs and s_is < scraps + recs * 3:
            partner_item_list.extend(self.__get_metal(
                scraps=0, recs=0, refs=refs + 1, inv=partner_inv))
            my_item_list.extend(self.__get_metal_for_trade_enough(9 - (recs * 3 + scraps), my_inv))
        elif rf_is < refs and rc_is >= need_rec and s_is >= need_scrap + (need_rec - rc_is) * 3:
            partner_item_list.extend(self.__get_metal(
                scraps=0, recs=need_rec + 1, refs=rf_is, inv=partner_inv))
            my_item_list.extend(self.__get_metal_for_trade_enough(need_rec - need_scrap, my_inv))
        else:
            partner_item_list.extend(self.__get_metal_for_trade_enough(price, partner_inv))
        return partner_item_list, my_item_list

    def sell(self, price_metal: int, item_asset_id: list[tuple[str, int]]) -> requests.Response:
        """
        Note: sells only one item.
        :param price_metal:
        :param item_asset_id: list of tuple(item asset id, amount)
        :return:
        """
        if self.partner.inventory.count_currency()['metal'] < price_metal:
            raise NotEnoughMetalException("Partner doesn't have enough metal.")
        partners_item_list = []
        my_item_list = item_asset_id
        refs, recs, scraps = scrap_to_ref_rec_scrap(price_metal)
        partner_to_add, me_to_add = self.__get_metal_for_trade(refs, recs, scraps, price_metal,
                                                               self.partner.trade_inventory, self.me.inventory)
        partners_item_list.extend(partner_to_add)
        my_item_list.extend(me_to_add)
        return self.send_trade(my_item_list, partners_item_list)

    def __read_trade_items(self, asset_list: list, inventory: dict) -> list:
        trade_item_list = []
        for asset in asset_list:
            assetid = asset["assetid"]
            classid = inventory["rgInventory"][assetid]["classid"]
            instanceid = inventory["rgInventory"][assetid]["instanceid"]
            def_index = inventory["rgDescriptions"][f"{classid}_{instanceid}"]["app_data"]["def_index"]
            trade_item_list.append(
                {"def_index": def_index, "classid": classid, "assetid": assetid, "amount": asset["amount"]})
        return trade_item_list

    def __get_trade_items(self, tradeoffer_id: str) -> dict:
        """
        Note: used only for incoming offers
        :param tradeoffer_id: id of an incoming trade offer
        :return: dictionary of items in trade:
        {
            'me': [
            {
                'def_index': str,
                'classid': str,
                'assetid': str,
                'amount': str
            },
            {
                'def_index': str,
                'classid': str,
                'assetid': str,
                'amount': str
            }],
            'them': [
            {
                'def_index': str,
                'classid': str,
                'assetid': str,
                'amount': str
            },
            {
                'def_index': str,
                'classid': str,
                'assetid': str,
                'amount': str
            }]
        }
        """
        response = session.get(f"https://steamcommunity.com/tradeoffer/{tradeoffer_id}/")
        currentTradeStatus = json.loads(re.findall(r'g_rgCurrentTradeStatus = (.*);', response.text)[0])
        me: list[dict] = self.__read_trade_items(currentTradeStatus["me"]["assets"], self.me.inventory.inventory)
        them: list[dict] = self.__read_trade_items(currentTradeStatus["them"]["assets"],
                                                   self.partner.trade_inventory.inventory)
        self.trade_items = {"me": me, "them": them}
        return self.trade_items

    def __count_metal(self, trade_list: list, key_price: int) -> int:
        count = 0
        for item in trade_list:
            if item["def_index"] == Currencies.SCRAP.get_def_index():
                count += 1
            if item["def_index"] == Currencies.RECLAIMED.get_def_index():
                count += 3
            if item["def_index"] == Currencies.REFINED.get_def_index():
                count += 9
            if item["def_index"] == Currencies.KEY.get_def_index():
                # count += (math.trunc(float(key_price)) * 9 + int(
                #     math.trunc((float(key_price) * 10)) % 10))
                count += key_price
        return count

    # todo SUPPORTS ONLY ONE ITEM TO BE BOUGHT
    def get_transaction_details(self, tradeoffer_id: str, key_price: int = 0) -> dict:
        """

        :param tradeoffer_id:
        :param key_price: key price in metal
        :return:
        {
            "me": price in metal (int),
            "them": list of {"def_index": , "classid": , "assetid": , "amount": }}
        """
        self.__get_trade_items(tradeoffer_id)
        me = self.__count_metal(self.trade_items["me"], key_price) - self.__count_metal(self.trade_items["them"],
                                                                                        key_price)
        them = []
        for item in self.trade_items["them"]:
            if item["def_index"] != Currencies.SCRAP.get_def_index() and \
                    item["def_index"] != Currencies.RECLAIMED.get_def_index() and \
                    item["def_index"] != Currencies.REFINED.get_def_index() and \
                    item["def_index"] != Currencies.KEY.get_def_index():
                them.append(item)
        return {"me": me, "them": them}

    def accept(self, tradeoffer_id: str):
        request_url = f"https://steamcommunity.com/tradeoffer/{tradeoffer_id}/accept"
        form = {
            "sessionid": get_session_id(),
            "serverid": 1,
            "tradeofferid": tradeoffer_id,
            "partner": self.partner.steam_id,
            # "captcha": ""
        }
        return session.request(RequestMethod.POST, request_url,
                               #                     {
                               #     'form': form,
                               #     'json': True,
                               #     'headers': {
                               #         'Referer': f'https://steamcommunity.com/tradeoffer/{tradeoffer_id}/',
                               #         'Host': 'steamcommunity.com',
                               #         'Connection': 'keep-alive',
                               #         'Content-Length': '104',
                               #         'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
                               #         'Accept': '*/*',
                               #         'DNT': '1',
                               #         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                               #         'sec-ch-ua-mobile': '?0',
                               #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                               #                       '(KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
                               #         'sec-ch-ua-platform': "Windows",
                               #         'Origin': 'https://steamcommunity.com',
                               #         'Sec-Fetch-Site': 'same-origin',
                               #         'Sec-Fetch-Mode': 'cors',
                               #         'Sec-Fetch-Dest': 'empty',
                               #         'Accept-Encoding': 'gzip, deflate, br',
                               #         'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7,ru;q=0.6,uk;q=0.5'
                               #     },
                               #     'checkJsonError': False,
                               #     'checkHttpError': False
                               # }
                               data=form,
                               json=True,
                               headers={
                                   'Referer': f'https://steamcommunity.com/tradeoffer/{tradeoffer_id}/',
                                   'Host': 'steamcommunity.com',
                                   # 'Connection': 'keep-alive',
                                   # 'Content-Length': '104',
                                   # 'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
                                   # 'Accept': '*/*',
                                   # 'DNT': '1',
                                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                   # 'sec-ch-ua-mobile': '?0',
                                   # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                   #               '(KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
                                   # 'sec-ch-ua-platform': "Windows",
                                   # 'Origin': 'https://steamcommunity.com',
                                   # 'Sec-Fetch-Site': 'same-origin',
                                   # 'Sec-Fetch-Mode': 'cors',
                                   # 'Sec-Fetch-Dest': 'empty',
                                   # 'Accept-Encoding': 'gzip, deflate, br',
                                   # 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7,ru;q=0.6,uk;q=0.5'
                               }
                               # checkJsonError=False,
                               # checkHttpError=False  # we'll check it ourself. Some trade offer errors return HTTP 500
                               )
