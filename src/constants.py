# card sizes
CARD_WIDTH = 1500
CARD_HEIGHT = 2100
BATTLE_CARD_MULT = 1.34

# the names of the .csv files that hold all the card information
CARDS = "spreadsheets/The One Set Cards Ranked - Card Ratings.csv"
TOKENS = "spreadsheets/The One Set Cards Ranked - Tokens.csv"
TRANSFORM_BACKSIDES = "spreadsheets/The One Set Cards Ranked - Transform Backsides.csv"
BASIC_LANDS = "spreadsheets/The One Set Cards Ranked - Basic Lands.csv"
ALT_ARTS = "spreadsheets/The One Set Cards Ranked - Alt Arts.csv"

# which columns in the spreadsheet correspond to which attribute
CARD_NAME = "Card Name"
FRONT_CARD_NAME = "Front Card Name"
DESCRIPTOR = "Descriptor"
CARD_RARITY = "Rarity"
CARD_COLOR = "Color Identity"
CARD_TYPES = "Type(s)"
CARD_SUBTYPES = "Subtype(s)"
CARD_SUPERTYPES = "Supertype(s)"
CARD_DATE = "Date Created"
ARCHETYPE = "Archetype"
UPDATED = "Updated"
FRONT_CARD_DESCRIPTOR = "Front Card Descriptor"

CHAR_TO_TITLE_CHAR = {
    "<": "{BC}",
    ">": "{FC}",
    ":": "{C}",
    '"': "{QT}",
    "/": "{FS}",
    "\\": "{BS}",
    "|": "{B}",
    "?": "{QS}",
    "*": "{A}",
}

NUMBER_WIDTHS = {
    "0": 26,
    "1": 14,
    "2": 23,
    "3": 22,
    "4": 25,
    "5": 22,
    "6": 23,
    "7": 21,
    "8": 23,
    "9": 25,
}

COLORS = {"W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green"}

POKER_BORDERS = {
    "W": "fold",
    "U": "echo",
    "B": "necro",
    "R": "joker",
    "G": "wild",
    "Colorless": "glass",
}

# tiling
TILING_WIDTH = 6
TILING_HEIGHT = 4
