# DEPRECATED: Apparently this dataset no longer exists
BASE_DATASET_NAME = "milesh1/35-million-chess-games"
BASE_DATASET_FILE_NAME = "all_with_filtered_anotations_since1998"
CLEANED_SUFFIX = "cleaned"
DATASET_FILE_EXTENSION = "csv"
DATASET_NAME = "pgn-tokenizer"

SEED = 1997
VOCAB_SIZE = 4096

TOKENIZER_CHUNK_PATTERN = r""" ?\d+\.|\. ?| ?[-\w]+|[#+]\s+"""

SPECIAL_TOKEN_PRE = "["
SPECIAL_TOKEN_POST = "]"

SPECIAL_TOKENS = {
    "START": f"{SPECIAL_TOKEN_PRE}g_start{SPECIAL_TOKEN_POST}",
    "END": f"{SPECIAL_TOKEN_PRE}g_end{SPECIAL_TOKEN_POST}",
    "UNKNOWN": f"{SPECIAL_TOKEN_PRE}unknown{SPECIAL_TOKEN_POST}",
    "PAD": f"{SPECIAL_TOKEN_PRE}pad{SPECIAL_TOKEN_POST}",
}
