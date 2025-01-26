# Contributor Guide

**Note**: More coming soon. This is a work-in-progress and the underlying dataset was just deleted from Kaggle.

1. [Fork the `DVDAGames/pgn-tokenizer` repository](https://github.com/DVDAGames/pgn-tokenizer/fork):
2. Clone your fork:

```bash
git clone git@github.com:<your-username>/pgn-tokenizer.git
```

3. Install dependencies:

```bash
uv install
```

4. Make your changes:
5. Test your changes:

```bash
uv run pytest
```

6. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/)
7. Push to your fork:

```bash
git push origin <your-branch>
```

8. Create a [Pull Request](https://github.com/DVDAGames/pgn-tokenizer/compare)
9. Wait for review, approval, and a virtual high five.

## Development Scripts

There are a few scripts in the `scripts` directory that can be useful for development:

- `clean-dataset.py`: Cleans the original weirdness out of the dataset PGN notation
- `format-dataset-for-training.py`: Formats the cleaned dataset for tokenizer training by adding the special `[g_start]` and `[g_end]` tokens to the beginning and end of each game
- `train.py`: Trains the tokenizer on the formatted dataset and saves the model
