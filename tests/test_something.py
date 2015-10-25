import pytest
import kaolin

def test_fail():
    with pytest.raises(Exception):
        assert 1==2