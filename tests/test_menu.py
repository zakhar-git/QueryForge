import pytest

from queryforge.menu import Menu


def test_parse_indices():
    assert Menu.parse_indices("1,3,5-7", 10) == [1, 3, 5, 6, 7]
    assert Menu.parse_indices("7-5", 10) == [5, 6, 7]


def test_parse_indices_rejects_out_of_range():
    with pytest.raises(ValueError):
        Menu.parse_indices("1,11", 10)
