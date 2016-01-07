import pytest
import os

import pygit2
import gitdict.utils

from . import gitrepo


def example():
    with pytest.raises(Exception):
        assert 1==2
    assert 0


def test_dict_like_get_known_element():
    d = {'a': 'some value'}
    value = gitdict.utils.dict_like_get(d, 'a')
    assert value == 'some value'

def test_dict_like_get_unknown_element():
    d = dict()
    value = gitdict.utils.dict_like_get(d, 'a')
    assert value is None
    value = gitdict.utils.dict_like_get(d, 'a', default='b')
    assert value == 'b'

def test_ensure_oid_form_oid():
    something = pygit2.Oid(raw=b"1")
    value = gitdict.utils.ensure_oid(something)
    assert value == something

def test_ensure_oid_form_str():
    something = "1"
    value = gitdict.utils.ensure_oid(something)
    assert value == pygit2.Oid(hex=something)

def test_ensure_oid_form_bytes():
    something = b"1"
    value = gitdict.utils.ensure_oid(something)
    assert value == pygit2.Oid(raw=something)

def test_ensure_oid_form_pygit2_object(gitrepo):
    repo = gitdict.Repository(gitrepo)
    value = gitdict.utils.ensure_oid(repo._pg2_tree)
    assert value == repo._pg2_tree.id

def test_ensure_oid_form_raises_error():
    with pytest.raises(gitdict.GitDictError):
        assert gitdict.utils.ensure_oid(None)
        assert gitdict.utils.ensure_oid("x")
        assert gitdict.utils.ensure_oid(object())