import csv
from PIL import Image
from constants import (
    ALT_ARTS,
    BASIC_LANDS,
    CARD_COLOR,
    CARD_NAME,
    CARD_SUPERTYPES,
    CARD_TYPES,
    CARDS,
    CHAR_TO_TITLE_CHAR,
    COLORS,
    DESCRIPTOR,
    FRONT_CARD_DESCRIPTOR,
    FRONT_CARD_NAME,
    TOKENS,
    TRANSFORM_BACKSIDES,
)
from log import log


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

    token_descriptor = token[DESCRIPTOR].strip()
    if len(token_descriptor) > 0:
        token_descriptor = f" - {token_descriptor}"

    token_supertypes = token[CARD_SUPERTYPES]
    token_types = token[CARD_TYPES]
    return f"{token_color}{token_supertypes} {token[CARD_NAME]} {token_types}{token_descriptor}"


def process_spreadsheets() -> tuple[
    dict[str, dict[str, str | dict[str, str]]],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[str, dict[str, str | dict[str, str]]],
]:
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

    basic_lands = {}
    with open(BASIC_LANDS, "r", encoding="utf8") as basic_lands_sheet:
        basic_lands_sheet_reader = csv.reader(basic_lands_sheet)
        columns = next(basic_lands_sheet_reader)
        for row in basic_lands_sheet_reader:
            values = dict(zip(columns, row))
            if len(values[CARD_NAME]) > 0:
                full_basic_land_name = f"{values[CARD_NAME]} - {values[DESCRIPTOR]}"
                values[CARD_NAME] = full_basic_land_name
                basic_lands[full_basic_land_name] = values

    alt_arts = {}
    transform_backsides: list[dict[str, str]] = []
    with open(ALT_ARTS, "r", encoding="utf8") as alt_arts_sheet:
        alt_arts_sheet_reader = csv.reader(alt_arts_sheet)
        columns = next(alt_arts_sheet_reader)
        for row in alt_arts_sheet_reader:
            values = dict(zip(columns, row))
            if len(values[CARD_NAME]) > 0:
                full_alt_art_name = f"{values[CARD_NAME]} - {values[DESCRIPTOR]}"
                values[CARD_NAME] = full_alt_art_name

                front_card_name = values[FRONT_CARD_NAME].strip()
                if len(front_card_name) > 0:
                    full_front_card_name = (
                        f"{front_card_name} - {values[FRONT_CARD_DESCRIPTOR]}"
                    )
                    values[FRONT_CARD_NAME] = full_front_card_name
                    transform_backsides.append(values)
                else:
                    alt_arts[full_alt_art_name] = values

        for backside in transform_backsides:
            front_side_name = backside[FRONT_CARD_NAME]
            front_side = alt_arts[front_side_name]
            if not front_side.get("Transform Backsides", False):
                front_side["Transform Backsides"] = []
            front_side["Transform Backsides"].append(backside)

    return cards, tokens, basic_lands, alt_arts


def cardname_to_filename(card_name: str) -> str:
    file_name = card_name.replace("’", "'")
    for bad_char in CHAR_TO_TITLE_CHAR.keys():
        file_name = file_name.replace(bad_char, CHAR_TO_TITLE_CHAR[bad_char])
    return file_name


def open_card_file(
    file_name: str, card_path: str = "unprocessed_cards/"
) -> Image.Image | None:
    try:

        if len(file_name) > 0:
            base_card = Image.open(
                f"cards/{card_path}{file_name}.png"
            )
        else:
            return None

    except FileNotFoundError:

        try:
            new_file_name = file_name.replace("'", "’")
            base_card = Image.open(
                f"cards/{card_path}{new_file_name}.png"
            )
        except FileNotFoundError:
            log(f"""Couldn't find "{file_name}" in "{card_path}".""")
            return None

    return base_card
