"""Tests for kjb_llm.utils."""

from kjb_llm.utils import parse_verses


def test_parse_single_verse():
    line = "Genesis 1:1  In the beginning God created the heaven and the earth."
    verses = list(parse_verses(line))
    assert len(verses) == 1
    v = verses[0]
    assert v["book"] == "Genesis"
    assert v["chapter"] == 1
    assert v["verse"] == 1
    assert v["reference"] == "Genesis 1:1"
    assert v["text"].startswith("In the beginning")


def test_parse_numbered_book():
    line = "1 Samuel 3:10  And the LORD came, and stood, and called as at other times"
    verses = list(parse_verses(line))
    assert len(verses) == 1
    assert verses[0]["book"] == "1 Samuel"
    assert verses[0]["chapter"] == 3
    assert verses[0]["verse"] == 10


def test_parse_multiple_verses():
    text = (
        "Genesis 1:1  In the beginning God created the heaven and the earth.\n"
        "Genesis 1:2  And the earth was without form, and void.\n"
        "\n"
        "Genesis 1:3  And God said, Let there be light: and there was light.\n"
    )
    verses = list(parse_verses(text))
    assert len(verses) == 3
    assert verses[2]["reference"] == "Genesis 1:3"


def test_parse_empty_string():
    assert list(parse_verses("")) == []


def test_parse_non_verse_lines():
    text = "This is just a regular line.\nAnother line without a verse."
    assert list(parse_verses(text)) == []
