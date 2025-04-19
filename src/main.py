import csv
import argparse
from datetime import datetime
import os
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
UPDATED = "Updated"


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


def get_token_full_name(token: dict[str, str]) -> str:
    color = token[CARD_COLOR]
    token_color = ""
    if "Colorless" in color:
        token_color = "Colorless "
    else:
        for char in color.strip():
            try:
                token_color += f"{COLORS[char]} "
            except:
                log(f"""Token "{token[CARD_NAME]}" has an invalid color identity.""")
                token_color = ""
                break

    if len(token_color) == 0:
        log(f"""Token "{token[CARD_NAME]}" has an invalid color identity.""")
        return None

    token_supertypes = token[CARD_SUPERTYPES]
    token_types = token[CARD_TYPES]
    return f"{token_color}{token_supertypes} {token[CARD_NAME]} {token_types}"


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
                full_token_name = get_token_full_name(values)
                if full_token_name is not None:
                    values[CARD_NAME] = full_token_name
                    tokens[full_token_name] = values

    return cards, tokens


def cardname_to_filename(card_name: str) -> str:
    file_name = card_name.replace("’", "'")
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


def process_card(
    card: dict[str, str | dict[str, str]],
    card_num: int,
    num_cards: int,
    parent_card: dict[str, str | dict[str, str]] = None,
    indent: bool = False,
):
    file_name = cardname_to_filename(card[CARD_NAME])

    base_card = open_card_file(file_name)
    if base_card is None:
        return

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

    if parent_card is None:
        archetype = card[ARCHETYPE]
    else:
        archetype = parent_card[ARCHETYPE]

    if "Poker" in archetype:
        color = card[CARD_COLOR].strip()
        border = POKER_BORDERS.get(color, "black")
        card_overlay.add_layer(f"images/{frame_type}/borders/{border}.png")
    else:
        card_overlay.add_layer(f"images/{frame_type}/borders/black.png")

    card_overlay.add_layer(f"images/{frame_type}/collection/set_name.png")

    year = datetime.strptime(card[CARD_DATE], "%m/%d/%Y").year
    card_overlay.add_layer(f"images/{frame_type}/years/{year}.png")

    if parent_card is None:
        rarity = card[CARD_RARITY].lower()
    else:
        rarity = parent_card[CARD_RARITY].lower()

    card_overlay.add_layer(f"images/{frame_type}/rarities/{rarity}.png")

    number = str(card_num + 1).zfill(len(str(num_cards)))
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
    log(f"""{"\t" if indent else ""}Successfully processed "{card[CARD_NAME]}".""")


def process_token(token: dict[str, str], token_num: int, num_tokens: int):
    file_name = cardname_to_filename(token[CARD_NAME])

    base_token = open_card_file(file_name)
    if base_token is None:

        return

    token_overlay = Card()

    token_overlay.add_layer("images/standard/borders/black.png")

    token_overlay.add_layer("images/standard/collection/set_name.png")

    year = datetime.strptime(token[CARD_DATE], "%m/%d/%Y").year
    token_overlay.add_layer(f"images/standard/years/{year}.png")

    token_overlay.add_layer("images/standard/rarities/token.png")

    number = str(token_num + 1).zfill(len(str(num_tokens)))
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


def process_cards(
    cards: dict[str, dict[str, str | dict[str, str]]], only_updated: bool = False
):
    log(f"\n----- PROCESSING{" UPDATED" if only_updated else ""} CARDS -----\n")

    card_name_list = list(cards.keys())
    card_name_list.sort(
        key=lambda card_name: (
            datetime.strptime(cards[card_name][CARD_DATE], "%m/%d/%Y"),
            cards[card_name][CARD_NAME],
        )
    )

    for num, card_name in enumerate(card_name_list):
        card = cards[card_name]
        if only_updated and card[UPDATED] == "FALSE":
            continue

        process_card(card, num, len(cards))
        for backside in card["Transform Backsides"]:
            process_card(backside, num, len(cards), card, indent=True)


def process_tokens(tokens: dict[str, dict[str, str]]):
    log("\n----- PROCESSING TOKENS -----\n")

    token_name_list = list(tokens.keys())
    token_name_list.sort(
        key=lambda token_name: (
            datetime.strptime(tokens[token_name][CARD_DATE], "%m/%d/%Y"),
            tokens[token_name][CARD_NAME],
        )
    )

    for num, token_name in enumerate(token_name_list):
        token = tokens[token_name]
        process_token(token, num, len(tokens))


def find_files_not_in_spreadsheets(
    cards: dict[str, dict[str, str | dict[str, str]]], tokens: dict[str, dict[str, str]]
):
    """
    Finds the names of any files in cards/unprocessed_cards that aren't in the spreadsheet.
    """

    unprocessed_cards = [
        f[:-4].replace("’", "'")
        for f in os.listdir("cards/unprocessed_cards")
        if f.endswith(".png")
    ]

    card_names = []

    for card_name in cards.keys():
        card_names.append(cardname_to_filename(card_name))

        card = cards[card_name]
        for backside in card["Transform Backsides"]:
            card_names.append(cardname_to_filename(backside[CARD_NAME]))

    for token_name in tokens.keys():
        card_names.append(cardname_to_filename(token_name))

    extra1 = set(unprocessed_cards) - set(card_names)

    processed_cards = [
        f[:-4].replace("’", "'")
        for f in os.listdir("cards/processed_cards")
        if f.endswith(".png")
    ]

    extra2 = set(unprocessed_cards) - set(processed_cards)
    with open("report.txt", "w", encoding="utf8") as report_file:
        report_file.write("----- UNPROCESSED CARDS NOT IN SPREADSHEETS -----\n\n")
        for name in extra1:
            report_file.write(f"{name}\n")

        report_file.write("\n\n----- CARDS NOT PROCESSED -----\n\n")
        for name in extra2:
            report_file.write(f"{name}\n")


def main(
    do_cards: bool = True,
    do_tokens: bool = True,
    only_updated: bool = False,
    find_files: bool = False,
):
    reset_log()
    cards, tokens = process_spreadsheets()

    if do_cards:
        process_cards(cards, only_updated)
    if do_tokens:
        process_tokens(tokens)

    if find_files:
        find_files_not_in_spreadsheets(cards, tokens)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format The One Set cards.")

    parser.add_argument(
        "-nc",
        "--no-cards",
        action="store_false",
        help="Skip processing the regular cards.",
        dest="cards",
    )
    parser.add_argument(
        "-nt",
        "--no-tokens",
        action="store_false",
        help="Skip processing the tokens.",
        dest="tokens",
    )
    parser.add_argument(
        "-ou",
        "--only-updated",
        action="store_true",
        help="Only process cards that have been marked as updated on the spreadsheet.",
        dest="only_updated",
    )
    parser.add_argument(
        "-ff",
        "--find-files",
        action="store_true",
        help="Generate a report on which files in cards/unprocessed_cards aren't in the spreadsheets.",
        dest="find_files",
    )

    args = parser.parse_args()
    main(args.cards, args.tokens, args.only_updated, args.find_files)
