import csv
import argparse
from datetime import datetime
from PIL import Image

from log import log, reset_log
from model.Card import Card

# the names of the .csv files that hold all the card information
CARDS = "spreadsheets/cards.csv"
TOKENS = "spreadsheets/tokens.csv"
TRANSFORM_BACKSIDES = "spreadsheets/transform.csv"

# which columns in the spreadsheet correspond to which attribute
CARD_NAME = "Card Name"
FRONT_CARD_NAME = "Front Card Name"
CARD_RARITY = "Rarity"
CARD_COLOR = "Color Identity"
CARD_TYPES = "Type(s)"
CARD_SUBTYPES = "Subtype(s)"
CARD_SUPERTYPES = "Supertype(s)"
CARD_DATE = "Date Created"
ARCHETYPE = "Archetype"


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

POKER_BORDERS = {"W": "fold", "U": "echo", "B": "necro", "R": "joker", "G": "wild", "Colorless": "glass"}


def process_spreadsheets() -> (
    tuple[dict[str, dict[str, str | dict[str, str]]], dict[str, dict[str, str]]]
):
    cards = {}
    with open(CARDS, "r", encoding="utf8") as cards_sheet:
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

    tokens = {}
    with open(TOKENS, "r", encoding="utf8") as tokens_sheet:
        tokens_sheet_reader = csv.reader(tokens_sheet)
        columns = next(tokens_sheet_reader)
        for row in tokens_sheet_reader:
            values = dict(zip(columns, row))
            if len(values[CARD_NAME]) > 0:
                tokens[values[CARD_NAME]] = values

    return cards, tokens


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
            new_file_name = file_name.replace("'", "’")
            base_card = Image.open(f"cards/unprocessed_cards/{new_file_name}.png")
        except FileNotFoundError:
            log(f"""Couldn't find "{file_name}".""")
            return None

    return base_card


def process_cards(cards: dict[str, dict[str, str | dict[str, str]]]):
    log("----- PROCESSING CARDS -----\n")

    card_name_list = list(cards.keys())
    card_name_list.sort(
        key=lambda card_name: (
            datetime.strptime(cards[card_name][CARD_DATE], "%m/%d/%Y"),
            cards[card_name][CARD_NAME],
        )
    )

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

        archetype = card[ARCHETYPE]
        if "Poker" in archetype:
            color = card[CARD_COLOR].strip()
            border = POKER_BORDERS.get(color, "black")
            card_overlay.add_layer(f"images/{frame_type}/borders/{border}.png")
        else:
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
                card_overlay.add_layer(
                    f"images/{frame_type}/numbers/{char}.png",
                    position=(int(offset * width_mult), 0),
                )
            else:
                card_overlay.add_layer(
                    f"images/{frame_type}/numbers/{char}.png",
                    position=(0, int(offset * width_mult)),
                )
            offset += NUMBER_WIDTHS[char]

        card_overlay.add_layer(base_card, 0)

        final_card = card_overlay.merge_layers()
        final_card.save(f"cards/processed_cards/{file_name}.png")
        log(f"""Successfully processed "{card_name}".""")

        card_overlay.remove_layer(0)
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
            log(f"""\tSuccessfully processed "{tf_card_name}".""")


def process_tokens(tokens: dict[str, dict[str, str]]):
    log("----- PROCESSING TOKENS -----\n")

    token_name_list = list(tokens.keys())
    token_name_list.sort(
        key=lambda token_name: (
            datetime.strptime(tokens[token_name][CARD_DATE], "%m/%d/%Y"),
            tokens[token_name][CARD_NAME],
        )
    )

    for num, token_name in enumerate(token_name_list):

        token = tokens[token_name]

        color = token[CARD_COLOR]
        if "Colorless" in color:
            color = "Colorless "
        else:
            color = ""
            for char in color.strip():
                try:
                    color += f"{COLORS[char]} "
                except:
                    log(f'"{token_name}" has an invalid color identity.')
                    color = ""
                    break

        if len(color) == 0:
            continue

        token_supertypes = tokens[token_name][CARD_SUPERTYPES]
        token_types = tokens[token_name][CARD_TYPES]
        full_token_name = f"{color}{token_supertypes} {token_name} {token_types}"

        file_name = cardname_to_filename(full_token_name)

        base_token = open_card_file(file_name)
        if base_token is None:
            continue

        token_overlay = Card()

        token_overlay.add_layer("images/standard/borders/black.png")

        token_overlay.add_layer("images/standard/collection/set_name.png")

        year = datetime.strptime(token[CARD_DATE], "%m/%d/%Y").year
        token_overlay.add_layer(f"images/standard/years/{year}.png")

        number = str(num + 1).zfill(len(str(len(tokens))))
        offset = 0
        for char in number:
            token_overlay.add_layer(
                f"images/standard/numbers/{char}.png",
                position=(int(offset), 0),
            )
            offset += NUMBER_WIDTHS[char]

        token_overlay.add_layer(base_token, 0)

        final_token = token_overlay.merge_layers()
        final_token.save(f"cards/processed_cards/{file_name}.png")
        log(f"""Successfully processed "{file_name}".""")


def main(do_cards: bool = True, do_tokens: bool = True):
    cards, tokens = process_spreadsheets()
    if do_cards:
        process_cards(cards)
    if do_tokens:
        process_tokens(tokens)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format The One Set cards.")

    parser.add_argument(
        "-nc", "--no-cards",
        action="store_false",
        help="Skip processing the regular cards.",
        dest="cards"
    )
    parser.add_argument(
        "-nt", "--no-tokens",
        action="store_false",
        help="Skip processing the tokens.",
        dest="tokens"
    )

    args = parser.parse_args()
    main(args.cards, args.tokens)
