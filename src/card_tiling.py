"""
Takes the processed cards and tiles them.
"""

import argparse
from datetime import datetime
from PIL import Image

from common import cardname_to_filename, open_card_file, process_spreadsheets
from constants import (
    CARD_DATE,
    CARD_HEIGHT,
    CARD_NAME,
    CARD_TYPES,
    CARD_WIDTH,
    TILING_HEIGHT,
    TILING_WIDTH,
    UPDATED,
)
from log import log, reset_log
from model.Card import Card


def tile_cards(
    cards: dict[str, dict[str, str | dict[str, str]]],
    only_updated: bool = False,
    min_tile_num: int = 1,
    max_tile_num: int = float('inf'),
    quarantine: bool = True,
):
    log(f"\n----- PROCESSING{" UPDATED" if only_updated else ""} CARDS -----\n")

    card_name_list = list(cards.keys())
    card_name_list.sort(
        key=lambda card_name: (
            datetime.strptime(cards[card_name][CARD_DATE], "%m/%d/%Y"),
            cards[card_name][CARD_NAME],
        )
    )

    tile_num = 1
    tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)

    num = 0
    for card_name in card_name_list:
        card = cards[card_name]
        if only_updated and card[UPDATED] == "FALSE":
            continue

        tile_row = num // TILING_WIDTH
        tile_col = num % TILING_WIDTH

        if tile_num < min_tile_num:
            if tile_row == TILING_HEIGHT - 1 and tile_col == TILING_WIDTH - 1:
                log(f"Skipping Card Tile Set {tile_num}")
                tile_num += 1
                num = 0
            else:
                num += 1

            for backside in card["Transform Backsides"]:
                if tile_num < min_tile_num:
                    tile_row = num // TILING_WIDTH
                    tile_col = num % TILING_WIDTH

                    if tile_row == TILING_HEIGHT - 1 and tile_col == TILING_WIDTH - 1:
                        log(f"Skipping Card Tile Set {tile_num}")
                        tile_num += 1
                        num = 0
                    else:
                        num += 1
            continue

        if tile_num > max_tile_num:
            break

        log(f"""Tiling "{card_name}".""", do_print=False)

        file_name = cardname_to_filename(card_name)
        card_image = open_card_file(file_name, f"processed_cards/{"quarantine/" if quarantine else ""}")
        if card_image is None:
            continue

        if "Battle" in card[CARD_TYPES]:
            card_image = card_image.rotate(90, expand=True)
            card_image = card_image.resize(
                (CARD_WIDTH, CARD_HEIGHT), Image.Resampling.LANCZOS
            )

        try:
            tiles.add_layer(
                card_image, position=(tile_col * CARD_WIDTH, tile_row * CARD_HEIGHT)
            )
        except AttributeError:
            log(
                f"""Card file "{file_name}" cannot be opened or is otherwise corrupted."""
            )

        if tile_row == TILING_HEIGHT - 1 and tile_col == TILING_WIDTH - 1:
            finished_tiles = tiles.merge_layers()
            if finished_tiles is not None:
                log(f"\nCreating Card Tile Set {tile_num}.\n")
                finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}cards{tile_num}.png")
                tile_num += 1
            tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)
            num = 0
        else:
            num += 1

        for backside in card["Transform Backsides"]:

            backside_name = backside[CARD_NAME]
            log(f"""\tTiling "{backside_name}".""", do_print=False)

            tile_row = num // TILING_WIDTH
            tile_col = num % TILING_WIDTH

            file_name = cardname_to_filename(backside_name)
            backside_image = open_card_file(file_name, f"processed_cards/{"quarantine/" if quarantine else ""}")
            if backside_image is None:
                continue

            try:
                tiles.add_layer(
                    backside_image,
                    position=(tile_col * CARD_WIDTH, tile_row * CARD_HEIGHT),
                )
            except AttributeError:
                log(
                    f"""Card file "{file_name}" cannot be opened or is otherwise corrupted."""
                )

            if tile_row == TILING_HEIGHT - 1 and tile_col == TILING_WIDTH - 1:
                finished_tiles = tiles.merge_layers()
                if finished_tiles is not None:
                    log(f"\nCreating Card Tile Set {tile_num}.\n")
                    finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}cards{tile_num}.png")
                    tile_num += 1
                tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)
                num = 0
            else:
                num += 1

    finished_tiles = tiles.merge_layers()
    if finished_tiles is not None:
        log(f"\nCreating Card Tile Set {tile_num} (Final Tileset).\n")
        finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}cards{tile_num}.png")


def tile_tokens(tokens: dict[str, dict[str, str]], quarantine: bool = True):
    log(f"\n----- PROCESSING TOKENS -----\n")

    token_name_list = list(tokens.keys())
    token_name_list.sort(
        key=lambda token_name: (
            datetime.strptime(tokens[token_name][CARD_DATE], "%m/%d/%Y"),
            tokens[token_name][CARD_NAME],
        )
    )

    tile_num = 1
    tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)

    num = 0
    for token_name in token_name_list:

        log(f"""Tiling Token "{token_name}".""", do_print=False)

        tile_row = num // TILING_WIDTH
        tile_col = num % TILING_WIDTH

        file_name = cardname_to_filename(token_name)
        token_image = open_card_file(file_name, f"processed_cards/{"quarantine/" if quarantine else ""}")
        if token_image is None:
            continue

        try:
            tiles.add_layer(
                token_image, position=(tile_col * CARD_WIDTH, tile_row * CARD_HEIGHT)
            )
        except AttributeError:
            log(
                f"""Card file "{file_name}" cannot be opened or is otherwise corrupted."""
            )

        if tile_row == TILING_HEIGHT - 1 and tile_col == TILING_WIDTH - 1:
            finished_tiles = tiles.merge_layers()
            if finished_tiles is not None:
                log(f"\nCreating Token Tile Set {tile_num}.\n")
                finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}tokens{tile_num}.png")
                tile_num += 1
            tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)
            num = 0
        else:
            num += 1

    finished_tiles = tiles.merge_layers()
    if finished_tiles is not None:
        log(f"\nCreating Token Tile Set {tile_num} (Final Tileset).\n")
        finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}tokens{tile_num}.png")


def tile_basic_lands(basic_lands: dict[str, dict[str, str]], quarantine: bool = True):
    log(f"\n----- PROCESSING BASIC LANDS -----\n")

    basic_land_name_list = list(basic_lands.keys())
    basic_land_name_list.sort(
        key=lambda basic_land_name: (
            datetime.strptime(basic_lands[basic_land_name][CARD_DATE], "%m/%d/%Y"),
            basic_lands[basic_land_name][CARD_NAME],
        )
    )

    tile_num = 1
    tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)

    num = 0
    for basic_land_name in basic_land_name_list:

        log(f"""Tiling Basic Land "{basic_land_name}".""", do_print=False)

        tile_row = num // TILING_WIDTH
        tile_col = num % TILING_WIDTH

        file_name = cardname_to_filename(basic_land_name)
        basic_land_image = open_card_file(file_name, f"processed_cards/{"quarantine/" if quarantine else ""}")
        if basic_land_image is None:
            continue

        try:
            tiles.add_layer(
                basic_land_image,
                position=(tile_col * CARD_WIDTH, tile_row * CARD_HEIGHT),
            )
        except AttributeError:
            log(
                f"""Card file "{file_name}" cannot be opened or is otherwise corrupted."""
            )

        if tile_row == TILING_HEIGHT - 1 and tile_col == TILING_WIDTH - 1:
            finished_tiles = tiles.merge_layers()
            if finished_tiles is not None:
                log(f"\nCreating Basic Land Tile Set {tile_num}.\n")
                finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}basic_lands{tile_num}.png")
                tile_num += 1
            tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)
            num = 0
        else:
            num += 1

    finished_tiles = tiles.merge_layers()
    if finished_tiles is not None:
        log(f"\nCreating Basic Land Tile Set {tile_num} (Final Tileset).\n")
        finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}basic_lands{tile_num}.png")


def tile_alt_arts(
    alt_arts: dict[str, dict[str, str | dict[str, str]]], quarantine: bool = True
):
    log(f"\n----- PROCESSING CARDS -----\n")

    alt_art_name_list = list(alt_arts.keys())
    alt_art_name_list.sort(
        key=lambda alt_art_name: (
            datetime.strptime(alt_arts[alt_art_name][CARD_DATE], "%m/%d/%Y"),
            alt_arts[alt_art_name][CARD_NAME],
        )
    )

    tile_num = 1
    tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)

    num = 0
    for alt_art_name in alt_art_name_list:

        alt_art = alt_arts[alt_art_name]
        log(f"""Tiling "{alt_art_name}".""", do_print=False)

        tile_row = num // TILING_WIDTH
        tile_col = num % TILING_WIDTH

        file_name = cardname_to_filename(alt_art_name)
        alt_art_image = open_card_file(file_name, f"processed_cards/{"quarantine/" if quarantine else ""}")
        if alt_art_image is None:
            continue

        if "Battle" in alt_art[CARD_TYPES]:
            alt_art_image = alt_art_image.rotate(90, expand=True)
            alt_art_image = alt_art_image.resize(
                (CARD_WIDTH, CARD_HEIGHT), Image.Resampling.LANCZOS
            )

        try:
            tiles.add_layer(
                alt_art_image, position=(tile_col * CARD_WIDTH, tile_row * CARD_HEIGHT)
            )
        except AttributeError:
            log(
                f"""Card file "{file_name}" cannot be opened or is otherwise corrupted."""
            )

        if tile_row == TILING_HEIGHT - 1 and tile_col == TILING_WIDTH - 1:
            finished_tiles = tiles.merge_layers()
            if finished_tiles is not None:
                log(f"\nCreating Alt Art Tile Set {tile_num}.\n")
                finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}alt_arts{tile_num}.png")
                tile_num += 1
            tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)
            num = 0
        else:
            num += 1

        for backside in alt_art.get("Transform Backsides", []):

            backside_name = backside[CARD_NAME]
            log(f"""\tTiling "{backside_name}".""", do_print=False)

            tile_row = num // TILING_WIDTH
            tile_col = num % TILING_WIDTH

            file_name = cardname_to_filename(backside_name)
            backside_image = open_card_file(file_name, f"processed_cards/{"quarantine/" if quarantine else ""}")
            if backside_image is None:
                continue

            try:
                tiles.add_layer(
                    backside_image,
                    position=(tile_col * CARD_WIDTH, tile_row * CARD_HEIGHT),
                )
            except AttributeError:
                log(
                    f"""Card file "{file_name}" cannot be opened or is otherwise corrupted."""
                )

            if tile_row == TILING_HEIGHT - 1 and tile_col == TILING_WIDTH - 1:
                finished_tiles = tiles.merge_layers()
                if finished_tiles is not None:
                    log(f"\nCreating Alt Art Tile Set {tile_num}.\n")
                    finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}alt_arts{tile_num}.png")
                    tile_num += 1
                tiles = Card(CARD_WIDTH * TILING_WIDTH, CARD_HEIGHT * TILING_HEIGHT)
                num = 0
            else:
                num += 1

    finished_tiles = tiles.merge_layers()
    if finished_tiles is not None:
        log(f"\nCreating Alt Art Tile Set {tile_num} (Final Tileset).\n")
        finished_tiles.save(f"cards/card_tilings/{"quarantine/" if quarantine else ""}alt_arts{tile_num}.png")


def main(
    do_cards: bool = True,
    do_tokens: bool = True,
    do_basic_lands: bool = True,
    do_alt_arts: bool = True,
    only_updated: bool = False,
    starting_card_num: int = 1,
    ending_card_num: int = float('inf'),
    quarantine: bool = False,
):

    reset_log()
    cards, tokens, basic_lands, alt_arts = process_spreadsheets()

    if do_cards:
        tile_cards(cards, only_updated, starting_card_num, ending_card_num, quarantine)

    if do_tokens:
        tile_tokens(tokens, quarantine)

    if do_basic_lands:
        tile_basic_lands(basic_lands, quarantine)

    if do_alt_arts:
        tile_alt_arts(alt_arts, quarantine)


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
        "-scn",
        "--starting-card-num",
        type=int,
        default=1,
        help="Put all the cards generated into a quarantine folder.",
        dest="starting_card_num",
    )
    parser.add_argument(
        "-ecn",
        "--ending-card-num",
        type=int,
        default=float('inf'),
        help="Put all the cards generated into a quarantine folder.",
        dest="ending_card_num",
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
        args.starting_card_num,
        args.ending_card_num,
        args.quarantine,
    )
