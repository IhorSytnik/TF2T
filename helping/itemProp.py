from classes.multiValueEnum import MultiValueEnum


class Paint(MultiValueEnum):
    """
    Enum for paints

    First value - paint name
    Second value - hex value or red team hex value for team colours
    Third value - code for backpack.tf

    Note: is not used for now
    """
    # ENUM NAME_________________________________paint name______________________________________hex value___bp.tf code
    NOT_PAINTED =                               "",                                             "",         ""
    # Single colours
    ZEPHENIAHS_GREED =                          "Zepheniah's Greed",                            "424F3B",   "4345659"
    YE_OLDE_RUSTIC_COLOUR =                     "Ye Olde Rustic Colour",                        "7C6C57",   "8154199"
    THE_COLOR_OF_A_GENTLEMANNS_BUSINESS_PANTS = "The Color of a Gentlemann's Business Pants",   "F0E68C",   "15787660"
    THE_BITTER_TASTE_OF_DEFEAT_AND_LIME =       "The Bitter Taste of Defeat and Lime",          "32CD32",   "3329330"
    RADIGAN_CONAGHER_BROWN =                    "Radigan Conagher Brown",                       "694D3A",   "6901050"
    PINK_AS_HELL =                              "Pink as Hell",                                 "FF69B4",   "16738740"
    Peculiarly_Drab_Tincture =                  "Peculiarly Drab Tincture",                     "C5AF91",   "12955537"
    PECULIARLY_DRAB_TINCTURE =                  "Noble Hatter's Violet",                        "51384A",   "5322826"
    Muskelmannbraun =                           "Muskelmannbraun",                              "A57545",   "10843461"
    MUSKELMANNBRAUN =                           "Mann Co. Orange",                              "CF7336",   "13595446"
    INDUBITABLY_GREEN =                         "Indubitably Green",                            "729E42",   "7511618"
    DRABLY_OLIVE =                              "Drably Olive",                                 "808000",   "8421376"
    DARK_SALMON_INJUSTICE =                     "Dark Salmon Injustice",                        "E9967A",   "15308410"
    COLOR_NO_216_190_216 =                      "Color No. 216-190-216",                        "D8BED8",   "14204632"
    AUSTRALIUM_GOLD =                           "Australium Gold",                              "E7B53B",   "15185211"
    AN_EXTRAORDINARY_ABUNDANCE_OF_TINGE =       "An Extraordinary Abundance of Tinge",          "E6E6E6",   "15132390"
    AGED_MOUSTACHE_GREY =                       "Aged Moustache Grey",                          "7E7E7E",   "8289918"
    AFTER_EIGHT =                               "After Eight",                                  "2D2D24",   "2960676"
    A_MANNS_MINT =                              "A Mann's Mint",                                "BCDDB3",   "12377523"
    A_DISTINCTIVE_LACK_OF_HUE =                 "A Distinctive Lack of Hue",                    "141414",   "1315860"
    A_DEEP_COMMITMENT_TO_PURPLE =               "A Deep Commitment to Purple",                  "7D4071",   "8208497"
    A_COLOR_SIMILAR_TO_SLATE =                  "A Color Similar to Slate",                     "2F4F4F",   "3100495"
    # Team colour
    WATER_LOGGED_LAB_COAT =                     "Waterlogged Lab Coat",                         "A89A8C",   "11049612"
    THE_VALUE_OF_TEAMWORK =                     "The Value of Teamwork",                        "803020",   "8400928"
    TEAM_SPIRIT =                               "Team Spirit",                                  "B8383B",   "12073019"
    OPERATORS_OVERALLS =                        "Operator's Overalls",                          "483838",   "4732984"
    CREAM_SPIRIT =                              "Cream Spirit",                                 "C36C2D",   "12807213"
    BALACLAVAS_ARE_FOREVER =                    "Balaclavas Are Forever",                       "3B1F23",   "3874595"
    AN_AIR_OF_DEBONAIR =                        "An Air of Debonair",                           "654740",   "6637376"

    def get_name(self) -> str:
        return self._all_values[0]

    def get_hex(self) -> str:
        return "#" + self._all_values[1]

    def get_bp_code(self) -> str:
        return self._all_values[2]


class Quality(MultiValueEnum):
    """
    Enum for item qualities for searching

    First value - quality name (used for BackPack.tf)
    Second value - quality's numerical value (used for Scrap.tf)

    """
    # ENUM NAME_____quality name____numerical value
    NORMAL =        "Normal",       0
    GENUINE =       "Genuine",      1
    RARITY2 =       "rarity2",      2  # Unused
    VINTAGE =       "Vintage",      3
    RARITY4 =       "rarity4",      4  # Unused
    UNUSUAL =       "Unusual",      5
    UNIQUE =        "Unique",       6
    COMMUNITY =     "Community",    7
    VALVE =         "Valve",        8
    SELF_MADE =     "Self-Made",    9
    CUSTOMIZED =    "Customized",   10  # Unused
    STRANGE =       "Strange",      11
    COMPLETED =     "Completed",    12  # Unused
    HAUNTED =       "Haunted",      13
    COLLECTORS =    "Collector's",  14
    DECORATED =     "Decorated",    15

    def get_name(self) -> str:
        return self._all_values[0]

    def get_index(self) -> int:
        return self._all_values[1]
