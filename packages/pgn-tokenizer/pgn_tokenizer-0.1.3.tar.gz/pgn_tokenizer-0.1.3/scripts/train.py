import argparse

from datasets import load_from_disk
from tokenizers import Regex, Tokenizer
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from tokenizers.models import BPE
from tokenizers.normalizers import NFD
from tokenizers.pre_tokenizers import Split
from tokenizers.processors import ByteLevel as ByteLevelProcessor
from tokenizers.trainers import BpeTrainer

from pgn_tokenizer.constants import (
    DATASET_NAME,
    SPECIAL_TOKENS,
    TOKENIZER_CHUNK_PATTERN,
    VOCAB_SIZE,
)

TRAINING_DATA_PATH = f"./.data/datasets/{DATASET_NAME}/"
OUTPUT_PATH = "./src/pgn_tokenizer/config"

FULL_DATASET_PATH = f"{TRAINING_DATA_PATH}/full"
SAMPLE_DATASET_PATH = f"{TRAINING_DATA_PATH}/sample"

# get args from command line
parser = argparse.ArgumentParser()

parser.add_argument(
    "--sample",
    action="store_true",
    help="Use a smaller sample dataset for training",
)

parser.add_argument(
    "--vocab_size",
    help="Size of the vocabulary",
    default=VOCAB_SIZE,
)

args = parser.parse_args()

dataset = load_from_disk(
    dataset_path=SAMPLE_DATASET_PATH if args.sample else FULL_DATASET_PATH
)

print(f"Training {DATASET_NAME} with {'sample' if args.sample else 'full'} dataset...")

training_data = []

for x in dataset["train"].select_columns("PGN").to_list():
    training_data.append(x["PGN"])

tokenizer = Tokenizer(
    BPE(
        unk_token=SPECIAL_TOKENS["UNKNOWN"],
        fuse_unk=True,
        pad_token=SPECIAL_TOKENS["PAD"],
    )
)

tokenizer.normalizer = NFD()

tokenizer.pre_tokenizer = Split(
    pattern=Regex(TOKENIZER_CHUNK_PATTERN), behavior="isolated"
)

tokenizer.post_processor = ByteLevelProcessor(trim_offsets=True)
# this should remove the extra spaces inserted by the tokenization process
# which make the output not decode to the original input
tokenizer.decoder = ByteLevelDecoder()

trainer = BpeTrainer(
    vocab_size=args.vocab_size,
    show_progress=True,
    special_tokens=list(SPECIAL_TOKENS.values()),
)

tokenizer.train_from_iterator(training_data, trainer=trainer)

# save the vocab and merges files separately
tokenizer.model.save(OUTPUT_PATH, DATASET_NAME)

# save the tokenizer json output
tokenizer.save(f"{OUTPUT_PATH}/{DATASET_NAME}.json")
# save the vocab and merges files separately
tokenizer.model.save(OUTPUT_PATH, DATASET_NAME)

# save the tokenizer json output
tokenizer.save(f"{OUTPUT_PATH}/{DATASET_NAME}.json")
