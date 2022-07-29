# Key selling price in ref (should be set as the selling price on backpack.tf (*Amount they pay us))
KEY_SELLING_PRICE_REF = '58.77'

# An additional amount of buyers we can sell the item to
SAFE_PILLOW = 2

# Buyers we don't want to sell to
BLACKLIST = [
    '1217175197',  # wholesaler
]

# Category to parse on scrap.tf/hats:
# 0 - Recently Traded
# 1 - Strange Hats
# 2 - Higher-Value Hats
# 3 - Craft Hats
CATEGORY_NUMBER = 2

# Price cap in ref over which this parser can't go
PRICE_CAP = 315

# Info for inventories
TF2_APPID = 440
tf2_PRIMARY_CONTEXTID = '2'

HEADERS = {
    # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #
    # 'accept': 'text/html',
    # 'accept-encoding': 'utf-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    #
    # 'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7,ru;q=0.6,uk;q=0.5',
    # 'accept-language': 'en-GB,en;q=0.9,uk;q=0.8,en-US;q=0.7',
    # 'cache-control': 'no-cache',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'pragma': 'no-cache',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',

    # 'sec-ch-ua-mobile': '?0',
    # 'sec-ch-ua-platform': 'Windows',
    # 'sec-fetch-dest': 'document',
    # 'sec-fetch-mode': 'navigate',
    # 'sec-fetch-site': 'none',
    # 'sec-fetch-user': '?1',
    # 'upgrade-insecure-requests': '1',
}