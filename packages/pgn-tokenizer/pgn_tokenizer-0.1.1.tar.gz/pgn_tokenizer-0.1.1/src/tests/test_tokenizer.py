import pytest

from pgn_tokenizer import PGNTokenizer


@pytest.fixture(scope="session", autouse=True)
def setup_env():
    global tokenizer
    global test_string

    test_string = "1.d4 d5 2.Nf3 Bf5"
    tokenizer = PGNTokenizer()


def test_encode():
    encoded = tokenizer.encode(test_string)
    assert encoded == [49, 70, 172, 108, 98, 298]


def test_decode():
    decoded = tokenizer.decode([49, 70, 172, 108, 98, 298])
    assert decoded == test_string


def test_encode_decode():
    assert tokenizer.decode(tokenizer.encode(test_string)) == test_string
