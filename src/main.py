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
CARD_DATE = "Date Created"
CARD_RARITY = "Rarity"

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
    '0': 25,
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

def cardname_to_filename(cardname: str) -> str:
    filename = cardname
    for bad_char in CHAR_TO_TITLE_CHAR.keys():
        filename = filename.replace(bad_char, CHAR_TO_TITLE_CHAR[bad_char])
    return filename

def open_card_file(file_name: str) -> Image.Image | None:
    try:
        if len(file_name) > 0:
            base_card = Image.open(f"cards/unprocessed_cards/{file_name}.png")
        else:
            return None
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

        card_overlay = Card()

        # TODO: Decide a way to determine if card has special poker border
        card_overlay.add_layer("images/borders/black.png")

        card_overlay.add_layer("images/collection/set_name.png")

        year = datetime.strptime(card[CARD_DATE], "%m/%d/%Y").year
        card_overlay.add_layer(f"images/years/{year}.png")

        rarity = card[CARD_RARITY].lower()
        card_overlay.add_layer(f"images/rarities/{rarity}.png")

        number = str(num + 1).zfill(len(str(len(cards))))
        x_offset = 0
        for char in number:
            card_overlay.add_layer(f"images/numbers/{char}.png", position=(x_offset, 0))
            x_offset += NUMBER_WIDTHS[char]

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
