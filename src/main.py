import csv
from datetime import datetime
from PIL import Image

from model.Card import Card

# the names of the .csv files that hold all the card information
CARDS = "spreadsheets/cards.csv"
TOKENS = "spreadsheets/tokens.csv"
TRANSFORM_BACKSIDES = "spreadsheets/transform.csv"

# which columns in the spreadsheet correspond to which attribute
CARD_NAME = "Card Name"
FRONT_CARD_NAME = "Front Card Name"
CARD_RARITY = "Rarity"
CARD_TYPES = "Type(s)"
CARD_SUBTYPES = "Subtype(s)"
CARD_DATE = "Date Created"


CHAR_TO_TITLE_CHAR = {
    '<': '{BC}',
    '>': '{FC}',
    ':': '{C}',
    '"': '{QT}',
    '/': '{FS}',
    '\\': '{BS}',
    '|': '{B}',
    '?': '{QS}',
    '*': '{A}'
}

NUMBER_WIDTHS = {
    '0': 26,
    '1': 14,
    '2': 23,
    '3': 22,
    '4': 25,
    '5': 22,
    '6': 23,
    '7': 21,
    '8': 23,
    '9': 25
}

def process_spreadsheets() -> dict[str, dict[str, str | dict[str, str]]]:
    cards = {}
    with open(CARDS, 'r', encoding="utf8") as cards_sheet:
        cards_sheet_reader = csv.reader(cards_sheet)
        columns = next(cards_sheet_reader)
        for row in cards_sheet_reader:
            values = dict(zip(columns, row))
            if len(values[CARD_NAME]) > 0:
                values["Transform Backsides"] = []
                cards[values[CARD_NAME]] = values
    
    with open(TRANSFORM_BACKSIDES) as transform_sheet:
        transform_sheet_reader = csv.reader(transform_sheet)
        columns = next(transform_sheet_reader)
        for row in transform_sheet_reader:
            values = dict(zip(columns, row))
            if len(values[CARD_NAME]) > 0:
                cards[values[FRONT_CARD_NAME]]["Transform Backsides"].append(values)

    return cards

def cardname_to_filename(card_name: str) -> str:
    file_name = card_name
    for bad_char in CHAR_TO_TITLE_CHAR.keys():
        file_name = file_name.replace(bad_char, CHAR_TO_TITLE_CHAR[bad_char])
    return file_name

def open_card_file(file_name: str) -> Image.Image | None:
    try:

        if len(file_name) > 0:
            base_card = Image.open(f"cards/unprocessed_cards/{file_name}.png")
        else:
            return None
        
    except FileNotFoundError:

        try:
            file_name = file_name.replace("'", "’")
            base_card = Image.open(f"cards/unprocessed_cards/{file_name}.png")
        except FileNotFoundError:
            print(f"""Couldn't find "{file_name}".""")
            return None
        
    return base_card

def main():
    cards = process_spreadsheets()
    card_name_list = list(cards.keys())
    card_name_list.sort(key=lambda card_name: datetime.strptime(cards[card_name][CARD_DATE], "%m/%d/%Y"))

    for num, card_name in enumerate(card_name_list):

        card = cards[card_name]
        file_name = cardname_to_filename(card_name)

        base_card = open_card_file(file_name)
        if base_card is None:
            continue

        if "Battle" in card[CARD_TYPES]:
            frame_type = "wide_horizontal"
            card_width = 2814
            card_height = 2010
            width_mult = 1.34
            orientation = "horizontal"
        else:
            frame_type = "standard"
            card_width = 1500
            card_height = 2100
            width_mult = 1
            orientation = "vertical"

        card_overlay = Card(card_width, card_height)

        # TODO: Decide a way to determine if card has special poker border
        card_overlay.add_layer(f"images/{frame_type}/borders/black.png")

        card_overlay.add_layer(f"images/{frame_type}/collection/set_name.png")

        year = datetime.strptime(card[CARD_DATE], "%m/%d/%Y").year
        card_overlay.add_layer(f"images/{frame_type}/years/{year}.png")

        rarity = card[CARD_RARITY].lower()
        card_overlay.add_layer(f"images/{frame_type}/rarities/{rarity}.png")

        number = str(num + 1).zfill(len(str(len(cards))))
        offset = 0
        for char in number:
            if orientation == "vertical":
                card_overlay.add_layer(f"images/{frame_type}/numbers/{char}.png", position=(int(offset * width_mult), 0))
            else:
                card_overlay.add_layer(f"images/{frame_type}/numbers/{char}.png", position=(0, int(offset * width_mult)))
            offset += NUMBER_WIDTHS[char]

        for backside in card["Transform Backsides"]:
            tf_card_name = backside[CARD_NAME]
            tf_file_name = cardname_to_filename(tf_card_name)
            base_tf_card = open_card_file(tf_file_name)
            if base_tf_card is None:
                continue

            card_overlay.add_layer(base_tf_card, 0)
            final_card = card_overlay.merge_layers()
            card_overlay.remove_layer(0)
            final_card.save(f"cards/processed_cards/{tf_file_name}.png")
            print(f"""\tSuccessfully processed "{tf_card_name}".""")

        card_overlay.add_layer(base_card, 0)

        final_card = card_overlay.merge_layers()
        final_card.save(f"cards/processed_cards/{file_name}.png")
        print(f"""Successfully processed "{card_name}".""")

if __name__ == "__main__":
    main()
