import pytest
from eiopt.common import is_single_level_tuple


def test_is_single_level_tuple():
    assert is_single_level_tuple(([1,2],)) == False
    assert is_single_level_tuple(([1,2])) == False
    assert is_single_level_tuple((5,6)) == True
    assert is_single_level_tuple((5,(6,7))) == False
    assert is_single_level_tuple((5,(6,(7,8)))) == False
