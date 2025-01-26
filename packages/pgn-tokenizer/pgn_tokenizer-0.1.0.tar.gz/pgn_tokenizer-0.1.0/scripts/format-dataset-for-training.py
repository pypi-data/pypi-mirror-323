from datasets import Dataset, DatasetDict, load_dataset

from pgn_tokenizer.constants import (
    BASE_DATASET_FILE_NAME,
    BASE_DATASET_NAME,
    CLEANED_SUFFIX,
    DATASET_FILE_EXTENSION,
    DATASET_NAME,
    SEED,
    SPECIAL_TOKENS,
)

ORIGINAL_DATASET_FILE_PATH = f".data/datasets/{BASE_DATASET_NAME}/{BASE_DATASET_FILE_NAME}-{CLEANED_SUFFIX}.{DATASET_FILE_EXTENSION}"
FORMATTED_DATASET_PATH = f".data/datasets/{DATASET_NAME}/"

dataset = load_dataset("csv", data_files=ORIGINAL_DATASET_FILE_PATH)


# modify the PGN column to add the game start and game end tokens
def add_start_and_end_tokens(items: dict[str, list[str]]) -> dict[str, list[str]]:
    PGNs = items["PGN"]

    for i, pgn in enumerate(PGNs):
        if pgn is not None:
            items["PGN"][i] = SPECIAL_TOKENS["START"] + pgn + SPECIAL_TOKENS["END"]

    return items


def save_dataset(dataset: dict[str, Dataset], dataset_name: str) -> None:
    dataset_dict = DatasetDict(dataset)

    dataset_path = f"{FORMATTED_DATASET_PATH}/{dataset_name}"

    dataset_dict.save_to_disk(dataset_path)


# iterate through the dataset and add the start and end tokens
dataset["train"] = (
    dataset["train"]
    .filter(lambda x: x["PGN"] is not None)
    .map(lambda x: add_start_and_end_tokens(x), batched=True)
)

# generate a smaller sample dataset that can be used
# for quickly testing training and tokenization methods
sample = dataset["train"].train_test_split(
    test_size=1000, train_size=10000, shuffle=True, seed=SEED
)

# we'll cut out a test and validation set from the sample
sample_temp_dataset = sample["test"].train_test_split(test_size=0.5, seed=SEED)

# create a new DatasetDict for the sample
sample_dataset_dict = {
    "train": sample["train"],
    "test": sample_temp_dataset["train"],
    "validation": sample_temp_dataset["test"],
}

# save the sample dataset
save_dataset(sample_dataset_dict, "sample")

temp_dataset = dataset["train"].train_test_split(test_size=0.1, seed=SEED)

# create a new DatasetDict for the full dataset
dataset = {
    "train": temp_dataset["train"],
    "test": temp_dataset["train"],
    "validation": temp_dataset["test"],
}

# save the full dataset
save_dataset(dataset, "full")
