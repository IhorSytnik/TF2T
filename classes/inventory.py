from helping.currencies import Currencies
from helping.operations import get_metal_to_refs, get_metal_from_scraps_recs_refs


def get_inventory_without_currencies(inventory_dict: dict) -> dict:
    return {k: v for k, v in inventory_dict.items()
            if v['classid'] != Currencies.SCRAP.get_class_id() and
            v['classid'] != Currencies.RECLAIMED.get_class_id() and
            v['classid'] != Currencies.REFINED.get_class_id() and
            v['classid'] != Currencies.KEY.get_class_id()}


class Inventory:
    def __init__(self, inventory_dict):
        self.inventory: dict = inventory_dict
        self.start_inventory: dict = {}
        self._init_start_inventory()
        self._write_currency()

    def update_inventory(self, inventory_dict):
        """

        :param inventory_dict:
        :return: **True** - if old inventory and new one are equal, **False** - otherwise.
        """
        if self.inventory['rgInventory'] != inventory_dict['rgInventory']:
            self.inventory = inventory_dict
            self._write_currency()
            return True
        else:
            return False

    def _write_currency(self):
        inventory_values = self.get_rginventory().values()
        self.scraps = list(filter(lambda i: i['classid'] == Currencies.SCRAP.get_class_id(), inventory_values))
        self.recs = list(filter(lambda i: i['classid'] == Currencies.RECLAIMED.get_class_id(), inventory_values))
        self.refs = list(filter(lambda i: i['classid'] == Currencies.REFINED.get_class_id(), inventory_values))
        self.keys = list(filter(lambda i: i['classid'] == Currencies.KEY.get_class_id(), inventory_values))

    def count_currency(self) -> dict:
        metal = get_metal_from_scraps_recs_refs(len(self.scraps), len(self.recs), len(self.refs))
        ref_full = get_metal_to_refs(metal)
        return {'metal': metal, 'ref': ref_full}

    def _init_start_inventory(self):
        """
        Remembers start inventory, but without any currency.
        """
        self.start_inventory = get_inventory_without_currencies(self.get_rginventory())

    def get_rginventory(self):
        return self.inventory['rgInventory']

    def get_rgdescriptions(self):
        return self.inventory['rgDescriptions']

    def get_assetids_by_defindex_filtered(self, def_indexes: list[str]) -> list[str]:
        """
        Filtered, not to include items from the Inventory.start_inventory.

        :param def_indexes: list of items' asset ids
        :return: list of new items' asset ids.
        """
        item_ids = [(v['classid'], v['instanceid']) for v in self.get_rgdescriptions().values()
                    if v['app_data']['def_index'] in def_indexes]
        start_item_ids = [(v['classid'], v['instanceid']) for v in self.start_inventory.values()]
        items = list(filter(lambda i: (i['classid'], i['instanceid']) in item_ids and
                                      (i['classid'], i['instanceid']) not in start_item_ids,
                            self.get_rginventory().values()))
        return [item['id'] for item in items]

    def get_new_items(self, new_inventory: dict) -> dict:
        return {k: v for k, v in get_inventory_without_currencies(new_inventory).items()
                if k not in self.start_inventory}
