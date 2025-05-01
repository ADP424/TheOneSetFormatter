"""
Automatically adds collection info to cards based on our ranking spreadsheet.
"""

import argparse
from datetime import datetime
import os

from common import cardname_to_filename, open_card_file, process_spreadsheets
from constants import (
    ARCHETYPE,
    BATTLE_CARD_MULT,
    CARD_COLOR,
    CARD_DATE,
    CARD_NAME,
    CARD_RARITY,
    CARD_TYPES,
    NUMBER_WIDTHS,
    POKER_BORDERS,
    UPDATED,
)
from log import log, reset_log
from model.Card import Card


def process_card(
    card: dict[str, str | dict[str, str]],
    card_num: int,
    num_cards: int,
    parent_card: dict[str, str | dict[str, str]] = None,
    quarantine: bool = False,
):
    file_name = cardname_to_filename(card[CARD_NAME])

    base_card = open_card_file(file_name)
    if base_card is None:
        return

    if "Battle" in card[CARD_TYPES]:
        frame_type = "wide_horizontal"
        card_width = 2814
        card_height = 2010
        width_mult = BATTLE_CARD_MULT
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
        if len(color) == 1 and "Wastes" in archetype:
            border = f"glass_{border}"
        card_overlay.add_layer(f"images/{frame_type}/borders/poker/{border}.png")
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

    number = str(card_num).zfill(len(str(num_cards)))
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
    final_card.save(
        f"cards/processed_cards/{"quarantine/" if quarantine else ""}{file_name}.png"
    )
    log(
        f"""{"\t" if parent_card is not None else ""}Successfully processed "{card[CARD_NAME]}"."""
    )


def process_token(
    token: dict[str, str], token_num: int, num_tokens: int, quarantine: bool = False
):
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

    number = str(token_num).zfill(len(str(num_tokens)))
    offset = 0
    for char in number:
        token_overlay.add_layer(
            f"images/standard/numbers/{char}.png",
            position=(int(offset), 0),
        )
        offset += NUMBER_WIDTHS[char]

    token_overlay.add_layer(base_token, 0)

    final_token = token_overlay.merge_layers()
    final_token.save(
        f"cards/processed_cards/{"quarantine/" if quarantine else ""}{file_name}.png"
    )
    log(f"""Successfully processed "{file_name}".""")


def process_basic_land(
    basic_land: dict[str, str],
    basic_land_num: int,
    num_cards: int,
    quarantine: bool = False,
):
    file_name = cardname_to_filename(basic_land[CARD_NAME])

    base_basic_land = open_card_file(file_name)
    if base_basic_land is None:
        return

    basic_land_overlay = Card()

    basic_land_overlay.add_layer("images/standard/borders/black.png")

    basic_land_overlay.add_layer("images/standard/collection/set_name.png")

    year = datetime.strptime(basic_land[CARD_DATE], "%m/%d/%Y").year
    basic_land_overlay.add_layer(f"images/standard/years/{year}.png")

    basic_land_overlay.add_layer("images/standard/rarities/land.png")

    number = str(basic_land_num).zfill(len(str(num_cards)))
    offset = 0
    for char in number:
        basic_land_overlay.add_layer(
            f"images/standard/numbers/{char}.png",
            position=(int(offset), 0),
        )
        offset += NUMBER_WIDTHS[char]

    basic_land_overlay.add_layer(base_basic_land, 0)

    final_basic_land = basic_land_overlay.merge_layers()
    final_basic_land.save(
        f"cards/processed_cards/{"quarantine/" if quarantine else ""}{file_name}.png"
    )
    log(f"""Successfully processed "{file_name}".""")


def process_alt_art(
    alt_art: dict[str, str],
    alt_art_num: int,
    num_alt_arts: int,
    parent_alt_art: dict[str, str] = None,
    quarantine: bool = False,
):
    file_name = cardname_to_filename(alt_art[CARD_NAME])

    base_alt_art = open_card_file(file_name)
    if base_alt_art is None:
        return

    if "Battle" in alt_art[CARD_TYPES]:
        frame_type = "wide_horizontal"
        card_width = 2814
        card_height = 2010
        width_mult = BATTLE_CARD_MULT
        orientation = "horizontal"
    else:
        frame_type = "standard"
        card_width = 1500
        card_height = 2100
        width_mult = 1
        orientation = "vertical"

    alt_art_overlay = Card(card_width, card_height)

    if parent_alt_art is None:
        archetype = alt_art[ARCHETYPE]
    else:
        archetype = parent_alt_art[ARCHETYPE]

    if "Poker" in archetype:
        color = alt_art[CARD_COLOR].strip()
        border = POKER_BORDERS.get(color, "black")
        alt_art_overlay.add_layer(f"images/{frame_type}/borders/{border}.png")
    else:
        alt_art_overlay.add_layer(f"images/{frame_type}/borders/black.png")

    alt_art_overlay.add_layer(f"images/{frame_type}/borders/black.png")

    alt_art_overlay.add_layer(f"images/{frame_type}/collection/set_name.png")

    year = datetime.strptime(alt_art[CARD_DATE], "%m/%d/%Y").year
    alt_art_overlay.add_layer(f"images/{frame_type}/years/{year}.png")

    rarity = alt_art[CARD_RARITY].lower()
    alt_art_overlay.add_layer(f"images/{frame_type}/rarities/{rarity}.png")

    number = str(alt_art_num).zfill(len(str(num_alt_arts)))
    offset = 0
    for char in number:
        if orientation == "vertical":
            alt_art_overlay.add_layer(
                f"images/{frame_type}/numbers/{char}.png",
                position=(int(offset) * width_mult, 0),
            )
        else:
            alt_art_overlay.add_layer(
                f"images/{frame_type}/numbers/{char}.png",
                position=(0, int(offset * width_mult)),
            )
        offset += NUMBER_WIDTHS[char]

    if "Foil" in file_name:
        alt_art_overlay.add_layer(f"images/{frame_type}/overlays/foil.png")

    alt_art_overlay.add_layer(base_alt_art, 0)

    final_alt_art = alt_art_overlay.merge_layers()
    final_alt_art.save(
        f"cards/processed_cards/{"quarantine/" if quarantine else ""}{file_name}.png"
    )
    log(
        f"""{"\t" if parent_alt_art is not None else ""}Successfully processed "{file_name}"."""
    )


def process_cards(
    cards: dict[str, dict[str, str | dict[str, str]]],
    num_cards: int,
    only_updated: bool = False,
    card_names_to_process: list[str] = None,
    quarantine: bool = False,
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
        if card_names_to_process is not None and card_name not in card_names_to_process:
            continue

        card = cards[card_name]
        if only_updated and card[UPDATED] == "FALSE":
            continue

        process_card(card, num + 1, len(cards), quarantine=quarantine)
        for backside in card["Transform Backsides"]:
            process_card(backside, num + 1, num_cards, parent_card=card, quarantine=quarantine)


def process_tokens(
    tokens: dict[str, dict[str, str]],
    num_tokens: int,
    card_names_to_process: list[str] = None,
    quarantine: bool = False,
):
    log("\n----- PROCESSING TOKENS -----\n")

    token_name_list = list(tokens.keys())
    token_name_list.sort(
        key=lambda token_name: (
            datetime.strptime(tokens[token_name][CARD_DATE], "%m/%d/%Y"),
            tokens[token_name][CARD_NAME],
        )
    )

    for num, token_name in enumerate(token_name_list):
        if (
            card_names_to_process is not None
            and token_name not in card_names_to_process
        ):
            continue

        token = tokens[token_name]
        process_token(token, num + 1, num_tokens, quarantine=quarantine)


def process_basic_lands(
    basic_lands: dict[str, dict[str, str]],
    num_cards: int,
    num_basic_lands: int,
    card_names_to_process: list[str] = None,
    quarantine: bool = False,
):
    log("\n----- PROCESSING BASIC LANDS -----\n")

    basic_land_name_list = list(basic_lands.keys())
    basic_land_name_list.sort(
        key=lambda basic_land_name: (
            basic_lands[basic_land_name][CARD_NAME],
            datetime.strptime(basic_lands[basic_land_name][CARD_DATE], "%m/%d/%Y"),
        )
    )

    for num, basic_land_name in enumerate(basic_land_name_list):
        if (
            card_names_to_process is not None
            and basic_land_name not in card_names_to_process
        ):
            continue

        basic_land = basic_lands[basic_land_name]
        process_basic_land(
            basic_land, num_cards - num_basic_lands + num + 1, num_cards, quarantine=quarantine
        )


def process_alt_arts(
    alt_arts: dict[str, dict[str, str]],
    num_alt_arts: int,
    card_names_to_process: list[str] = None,
    quarantine: bool = False,
):
    log("\n----- PROCESSING ALT ARTS -----\n")

    alt_arts_name_list = list(alt_arts.keys())
    alt_arts_name_list.sort(
        key=lambda alt_art_name: (
            datetime.strptime(alt_arts[alt_art_name][CARD_DATE], "%m/%d/%Y"),
            alt_arts[alt_art_name][CARD_NAME],
        )
    )

    for num, alt_art_name in enumerate(alt_arts_name_list):
        if (
            card_names_to_process is not None
            and alt_art_name not in card_names_to_process
        ):
            continue

        alt_art = alt_arts[alt_art_name]
        process_alt_art(alt_art, num + 1, num_alt_arts, quarantine=quarantine)
        for backside in alt_art.get("Transform Backsides", []):
            process_alt_art(backside, num + 1, num_alt_arts, parent_alt_art=alt_art, quarantine=quarantine)


def generate_report(
    cards: dict[str, dict[str, str | dict[str, str]]],
    tokens: dict[str, dict[str, str]],
    basic_lands: dict[str, dict[str, str]],
    alt_arts: dict[str, dict[str, str | dict[str, str]]],
):
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

    for basic_land_name in basic_lands.keys():
        card_names.append(cardname_to_filename(basic_land_name))

    for alt_art_name in alt_arts.keys():
        card_names.append(cardname_to_filename(alt_art_name))

        alt_art = alt_arts[alt_art_name]
        for backside in alt_art.get("Transform Backsides", []):
            card_names.append(cardname_to_filename(backside[CARD_NAME]))

    extra1 = set(unprocessed_cards) - set(card_names)

    processed_cards = [
        f[:-4].replace("’", "'")
        for f in os.listdir("cards/processed_cards")
        if f.endswith(".png")
    ]

    extra2 = set(unprocessed_cards) - set(processed_cards)

    quarantined_processed_cards = [
        f[:-4].replace("’", "'")
        for f in os.listdir("cards/processed_cards/quarantine")
        if f.endswith(".png")
    ]

    extra3 = set(unprocessed_cards) - set(processed_cards) - set(quarantined_processed_cards)

    with open("report.txt", "w", encoding="utf8") as report_file:
        report_file.write("----- UNPROCESSED CARDS NOT IN SPREADSHEETS -----\n\n")
        for name in extra1:
            report_file.write(f"{name}\n")

        report_file.write("\n\n----- CARDS NOT PROCESSED NORMALLY -----\n\n")
        for name in extra2:
            report_file.write(f"{name}\n")

        report_file.write("\n\n----- CARDS NOT PROCESSED NORMALLY OR QUARANTINED -----\n\n")
        for name in extra3:
            report_file.write(f"{name}\n")

        report_file.write("\n\n----- PROCESSED CARDS BOTH IN AND OUT OF QUARANTINE -----\n\n")
        for name in quarantined_processed_cards:
            if name in processed_cards:
                report_file.write(f"{name}\n")

    log("\n----- PROCESSED REPORT -----\n")


def main(
    do_cards: bool = True,
    do_tokens: bool = True,
    do_basic_lands: bool = True,
    do_alt_arts: bool = True,
    only_updated: bool = False,
    report: bool = False,
    card_names_to_process: list[str] = None,
    quarantine: bool = False,
):
    reset_log()
    cards, tokens, basic_lands, alt_arts = process_spreadsheets()

    num_mainline_cards = len(cards) + len(basic_lands)
    num_tokens = len(tokens)
    num_basic_lands = len(basic_lands)
    num_alt_arts = len(alt_arts)

    if do_cards:
        process_cards(
            cards, num_mainline_cards, only_updated, card_names_to_process, quarantine
        )
    if do_tokens:
        process_tokens(tokens, num_tokens, card_names_to_process, quarantine)
    if do_basic_lands:
        process_basic_lands(
            basic_lands,
            num_mainline_cards,
            num_basic_lands,
            card_names_to_process,
            quarantine,
        )
    if do_alt_arts:
        process_alt_arts(alt_arts, num_alt_arts, card_names_to_process, quarantine)

    if report:
        generate_report(cards, tokens, basic_lands, alt_arts)


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
        "-nbl",
        "--no-basic-lands",
        action="store_false",
        help="Skip processing the basic lands.",
        dest="basic_lands",
    )
    parser.add_argument(
        "-naa",
        "--no-alt-arts",
        action="store_false",
        help="Skip processing the alternate arts of cards.",
        dest="alt_arts",
    )
    parser.add_argument(
        "-ou",
        "--only-updated",
        action="store_true",
        help="Only process cards that have been marked as updated on the spreadsheet.",
        dest="only_updated",
    )
    parser.add_argument(
        "-r",
        "--report",
        action="store_true",
        help="Generate a report of the state of the 'cards' directory.",
        dest="report",
    )
    parser.add_argument(
        "-cn",
        "--card-names",
        nargs="+",
        help="Only process the cards (including tokens, alt arts, etc.) with these names.",
        dest="card_names_to_process",
    )
    parser.add_argument(
        "-q",
        "--quarantine",
        action="store_true",
        help="Put all the cards generated into a quarantine folder.",
        dest="quarantine",
    )

    args = parser.parse_args()
    main(
        args.cards,
        args.tokens,
        args.basic_lands,
        args.alt_arts,
        args.only_updated,
        args.report,
        args.card_names_to_process,
        args.quarantine,
    )
