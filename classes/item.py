from dataclasses import dataclass

from helping.item_prop import Quality, Paint


@dataclass
class PriceFull:
    keys: int
    refs: float


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


@dataclass
class Item:
    """
    Example:
    Item(
        name='Strange Spiky Viking',\n
        name_base='Spiky Viking',\n
        item_id='11877542803',\n
        price_scrap=44,\n
        price_scrap_ref=4.88,\n
        price_scrap_full=PriceScrapFull(
                keys=0, refs=4.88
            ),
        painted=<Paint.BALACLAVAS_ARE_FOREVER: 'Balaclavas Are Forever', '#3B1F23'>\n
        def_index='31100',\n
        quality=<Quality.UNIQUE: 'Unique', 6>,\n
        craftable=False,\n
        available=1,\n
        bots={
                '21': 1,\n
                '23': 2,
            },
        offers=[
            Offer(
                price_backpack_keys=0,\n
                price_backpack_refs=5.0,\n
                price_backpack_metal=45,\n
                diff_metal=1,\n
                diff_ref=0.11,\n
                steam_id='75374747458787686',\n
                trade_id='187687686',\n
                trade_token='ZbF1-Dff',\n
                trade_offer_link='https://steamcommunity.com/tradeoffer/new/?partner=187687686&token=ZbF1-Dff'
            ),
        ]
    )
    """
    name: str
    name_base: str
    item_id: str
    price_scrap: int
    price_scrap_ref: float
    price_scrap_full: PriceFull
    painted: Paint
    def_index: str
    quality: Quality
    craftable: bool
    available: int
    bots: dict
    offers: list[Offer]
