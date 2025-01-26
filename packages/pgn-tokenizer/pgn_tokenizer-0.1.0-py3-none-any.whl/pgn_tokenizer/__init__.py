import os
from pathlib import Path

from transformers import PreTrainedTokenizerFast

from pgn_tokenizer.constants import DATASET_NAME

# HACK: suppress the warning about pytorch, jax, et al. from transformers import logging
# because we are only importing a tokenizer and using the transformers library for the
# underlying PreTrainedFastTokenizer functionality
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

base_path = Path(__file__).parent

tokenizer_config_path = (base_path / f"config/{DATASET_NAME}.json").resolve()
tokenizer_vocab_path = (base_path / f"config/{DATASET_NAME}-vocab.json").resolve()
tokenzier_merges_path = (base_path / f"config/{DATASET_NAME}-merges.txt").resolve()


class PGNTokenizer:
    def __init__(self):
        self.tokenizer = PreTrainedTokenizerFast(
            tokenizer_file=str(tokenizer_config_path)
        )
        self.vocab_size = self.tokenizer.vocab_size
        self.encode = self.tokenizer.encode
        self.decode = self.tokenizer.decode
