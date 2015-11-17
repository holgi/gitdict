import pytest
import gitdict

from . import gitrepo

def test_fail(gitrepo):
    with pytest.raises(Exception):
        assert 1==2
    assert 0