## Setup

1. Download "The One Set Cards Ranked - Card Ratings" as a `.csv`.<br>
    1. Put it inside the `spreadsheets` folder.<br>

2. Repeat step 1 for the other card listing sheets.

3. Put every card you want to convert inside `cards/unprocessed_cards`.
    1. Make sure all `<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, and `*` characters have been replaced in the filename as follows (these are all illegal characters in Windows filenames):<br>
    `<`: `{BC}`<br>
    `>`: `{FC}`<br>
    `:`: `{C}`<br>
    `"`: `{QT}`<br>
    `/`: `{FS}`<br>
    `\\`: `{BS}`<br>
    `|`: `{B}`<br>
    `?`: `{QS}`<br>
    `*`: `{A}`

## Running the Program

1. `pip install -r requirements.txt`

2. Run `python main.py` from the root directory.
    1. Add `-nc` to skip processing the regular cards.
    2. Add `-nt` to skip processing the tokens.
    3. Add `-nbl` to skip processing the basic lands.
    4. Add `-ou` to only process cards that are marked as updated.
    5. Add `-ff` to generate a report of unprocessed cards.

3. All the cards should appear in `cards/processed_cards`.
    1. If you think a card should have been processed but wasn't, check `log.txt` for the filename it was looking for and make sure all the characters match.
