import pytest

from calendar_bot.config import _parse_ids


def test_parse_ids_accepts_several_users():
    assert _parse_ids("771342, 42") == (771342, 42)


def test_parse_ids_rejects_empty_list():
    with pytest.raises(ValueError):
        _parse_ids(" , ")
