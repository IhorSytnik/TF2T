from enum import Enum


class HatsCategory(Enum):
    """
    Category to parse on scrap.tf/hats:
    0 - Recently Traded
    1 - Strange Hats
    2 - Higher-Value Hats
    3 - Craft Hats
    """
    RECENTLY_TRADED =   0
    STRANGE =           1
    HIGHER_VALUE =      2
    CRAFT =             3
