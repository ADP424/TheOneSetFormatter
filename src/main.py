import csv
from datetime import datetime
from PIL import Image

from model.Card import Card

# the names of the .csv files that hold all the card information
CARDS = "spreadsheets/cards.csv"
LANDS = "spreadsheets/lands.csv"
TOKENS = "spreadsheets/tokens.csv"

# which columns in the spreadsheet correspond to which attribute
CARD_NAME = "Card Name"
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

def read_csv(filepath: str) -> list[dict[str, str]]:
    cards = []
    with open(filepath, 'r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file)
        columns = next(csv_reader)
        for row in csv_reader:
            cards.append(dict(zip(columns, row)))
    cards.sort(key=lambda card: datetime.strptime(card[CARD_DATE], "%m/%d/%Y"))
    return cards

def cardname_to_filename(cardname: str) -> str:
    filename = cardname
    for bad_char in CHAR_TO_TITLE_CHAR.keys():
        filename = filename.replace(bad_char, CHAR_TO_TITLE_CHAR[bad_char])
    return filename

def main():
    cards = read_csv(CARDS)

    for num, card in enumerate(cards):

        card_name = cardname_to_filename(card[CARD_NAME])
        try:
            if len(card_name) > 0:
                base_card = Image.open(f"cards/unprocessed_cards/{card_name}.png")
            else:
                continue
        except FileNotFoundError:
            print(f"""Couldn't find "{card[CARD_NAME]}".""")
            continue

        processed_card = Card()
        processed_card.add_layer(base_card)

        # TODO: Find way to determine if card has special poker border
        processed_card.add_layer(Image.open("images/borders/black.png"))

        processed_card.add_layer(Image.open("images/collection/set_name.png"))

        year = datetime.strptime(card[CARD_DATE], "%m/%d/%Y").year
        processed_card.add_layer(Image.open(f"images/years/{year}.png"))

        rarity = card[CARD_RARITY].lower()
        processed_card.add_layer(Image.open(f"images/rarities/{rarity}.png"))

        number = str(num + 1).zfill(len(str(len(cards))))
        x_offset = 0
        for char in number:
            processed_card.add_layer(f"images/numbers/{char}.png", position=(x_offset, 0))
            x_offset += NUMBER_WIDTHS[char]

        final_card = processed_card.merge_layers()
        final_card.save(f"cards/processed_cards/{card_name}.png")
        print(f"""Successfully processed "{card[CARD_NAME]}".""")

if __name__ == "__main__":
    main()
