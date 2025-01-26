# PGN Tokenizer

This is a Byte Pair Encoding (BPE) tokenizer for chess Portable Game Notation (PGN).

It is uses the [`tokenizers`](https://huggingface.co/docs/tokenizers/) library from Hugging Face for training the tokenizer and the [`transformers`](https://huggingface.co/docs/transformers/) library from Hugging Face for initializing the tokenizer from the pretrained tokenizer model for faster tokenization.

**Note**: This is part of a work-in-progress project to investigate how language models might understand chess without an engine or any chess-specific knowledge.

## Tokenizer Comparison

More traditional, language-focused BPE tokenizer implementations are not suited for PGN strings because they are more likely to break the actual moves apart.

For example `1.e4 Nf6` would likely be tokenized as `1`, `.`, `e`, `4`, ` N`, `f`, `6` or `1`, `.e`, `4`, ` `, ` N`, `f`, `6` depending on the tokenizer's vocabulary, but with the specialized PGN tokenizer it would be tokenized as `1.`, `e4`, ` Nf6`.

### Visualization

Here is a visualization of the vocabulary of this specialized PGN tokenizer compared to the BPE tokenizer vocabularies of the `cl100k_base` (the vocabulary for the `gpt-3.5-turbo` and `gpt-4` models' tokenizer) and the `o200k_base` (the vocabulary for the `gpt-4o` model's tokenizer):

#### PGN Tokenizer

![PGN Tokenizer Visualization](./docs/assets/pgn-tokenizer.png)

**Note**: The tokenizer was trained with ~2.8 Million chess games in PGN notation with a target vocabulary size of `4096`.

#### GPT-3.5-turbo and GPT-4 Tokenizers

![GPT-4 Tokenizer Visualization](./docs/assets/gpt-4-tokenizer.png)

#### GPT-4o Tokenizer

![GPT-4o Tokenizer Visualization](./docs/assets/gpt-4o-tokenizer.png)

These were all generated with a function adapted from an [educational Jupyter Notebook in the `tiktoken` repository](https://github.com/openai/tiktoken/blob/main/tiktoken/_educational.py#L186).

## Installation

You can install it with your package manager of choice:

### uv

```bash
uv add pgn-tokenizer
```

### pip

```bash
pip install pgn-tokenizer
```

## Usage

It exposes a simple interface with `.encode()` and `.decode()` methods, and a `.vocab_size` property, but you can also access the underlying `PreTrainedTokenizerFast` class from the `transformers` library via the `.tokenizer` property.

```python
from pgn_tokenizer import PGNTokenizer

# Initialize the tokenizer
tokenizer = PGNTokenizer()

# Tokenize a PGN string
tokens = tokenizer.encode("1.e4 Nf6 2.e5 Nd5 3.c4 Nb6")

# Decode the tokens back to a PGN string
decoded = tokenizer.decode(tokens)

# get vocab from underlying tokenizer class
vocab = tokenizer.tokenizer.get_vocab()
```

## Acknowledgements

- [@karpathy](https://github.com/karpathy) for the [Let's build the GPT Tokenizer tutorial](https://youtu.be/zduSFxRajkE)
- [Hugging Face](https://huggingface.co/) for the [`tokenizers`](https://huggingface.co/docs/tokenizers/) and [`transformers`](https://huggingface.co/docs/transformers/) libraries.
- Kaggle user [MilesH14](https://www.kaggle.com/milesh14), whoever you are for the now-missing dataset of 3.5 million chess games referenced in many places, including this [research documentation](https://chess-research-project.readthedocs.io/en/latest/)
