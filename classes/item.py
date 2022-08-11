from dataclasses import dataclass

from helping.item_prop import Quality, Paint


@dataclass
class PriceFull:
    keys: int
    refs: float

    def __eq__(self, other):
        if isinstance(other, PriceFull):
            return self.keys == other.keys and \
                   self.refs == other.refs
        return False


@dataclass
class Offer:
    price_backpack: PriceFull
    price_backpack_metal: int
    diff_metal: int
    diff_ref: float
    steam_id: str
    trade_id: str
    trade_token: str
    trade_offer_link: str

    def __eq__(self, other):
        if isinstance(other, Offer):
            return self.price_backpack == other.price_backpack and \
                   self.price_backpack_metal == other.price_backpack_metal and \
                   self.diff_metal == other.diff_metal and \
                   self.diff_ref == other.diff_ref and \
                   self.steam_id == other.steam_id and \
                   self.trade_id == other.trade_id and \
                   self.trade_token == other.trade_token and \
                   self.trade_offer_link == other.trade_offer_link
        return False


@dataclass
class Item:
    """
    """
    name: str
    name_base: str
    item_id: str
    price_scrap: int
    price_scrap_ref: float
    price_scrap_full: PriceFull
    painted: Paint
    def_index: str
    category: int
    quality: Quality
    craftable: bool
    available: int
    bots: dict
    offers: tuple[str, list[Offer]]

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name == other.name and \
                   self.name_base == other.name_base and \
                   self.painted == other.painted and \
                   self.def_index == other.def_index and \
                   self.category == other.category and \
                   self.quality == other.quality and \
                   self.craftable == other.craftable
        return False

    def __ge__(self, other):
        return self.price_scrap >= other.price_scrap

    def __le__(self, other):
        return self.price_scrap >= other.price_scrap
