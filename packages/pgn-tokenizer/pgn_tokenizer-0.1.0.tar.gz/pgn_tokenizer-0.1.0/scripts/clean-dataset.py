import datetime

import kagglehub
import polars as pl

from pgn_tokenizer.constants import (
    BASE_DATASET_FILE_NAME,
    BASE_DATASET_NAME,
    CLEANED_SUFFIX,
    DATASET_FILE_EXTENSION,
)

print(f"Sorry, the dataset {BASE_DATASET_NAME} no longer exists on kaggle.com.")
print(
    "Please use the pre-trained tokenizer that was generated from this dataset while we look for another suitable dataset."
)

# download the dataset from kaggle
path = kagglehub.dataset_download(BASE_DATASET_NAME)

filepath = f"{path}/{BASE_DATASET_FILE_NAME}.txt"

with open(filepath) as file:
    file_contents = file.read()

    # remove first five lines of the file
    unformattedGames = file_contents.split("\n")

    # this will store our formatted dataset
    formattedGames = []

    # iterate through the games and format them properly
    for line in unformattedGames:
        # the original dataset has games formatted with metadata up front
        # and then ` ### ` separating the notation from the metadata
        data = line.split(" ### ")

        if len(data) != 2:
            continue

        # we'll extract the date, result, and Elo from the metadata
        metadata = data[0].split(" ")
        game = data[1]

        date = metadata[1]
        result = metadata[2]
        whiteElo = metadata[3]
        blackElo = metadata[4]

        # the move notation in this dataset uses a `W1 d4 B1 d5 W2...` format
        # so we'll need to convert it into a more standardized `1.d4 d5 2...` format
        turns = game.split(" W")

        gameString = []

        # iterate through turns
        for i, turn in enumerate(turns):
            # split turn on on space
            moves = turn.split(" ")

            # iterate through moves
            for move in moves:
                move.strip()

                if not move:
                    continue

                if move[0] == "W":
                    moves[moves.index(move)] = move[1:]
                # if move starts with a B, remove the B and the number that follows
                elif move[0] == "B":
                    prefix = f"B{i + 1}."
                    moves[moves.index(move)] = move[len(prefix) :]
                else:
                    moves[moves.index(move)] = move

            # join the moves into a single string and add the moves to the game
            gameString.append(" ".join(moves))

    formattedGames.append(
        {
            "Date": date,
            "Result": result,
            "WhiteElo": whiteElo,
            "BlackElo": blackElo,
            "PGN": " ".join(gameString).strip(),
        }
    )

    df = pl.DataFrame(formattedGames)

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    # HACK: some games don't seem to have a valid PGN after we apply our transformation
    # let's filter those out until we can revisit what's causing it
    df.filter(pl.col("PGN").is_not_null()).write_csv(
        # write out our new CSV file with the cleaned dataset
        f"../.data/datasets/{BASE_DATASET_NAME}/{BASE_DATASET_FILE_NAME}-{CLEANED_SUFFIX}.{DATASET_FILE_EXTENSION}"
    )

    file.close()
