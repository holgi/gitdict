import pytest
import os

import pygit2
import gitdict

from . import gitrepo


def example():
    with pytest.raises(Exception):
        assert 1==2
    assert 0

def test_repository_initialization_bare_head(gitrepo):
    repo = gitdict.Repository(gitrepo)
    assert isinstance(repo._pg2_repo, pygit2.Repository)
    assert isinstance(repo._pg2_tree, pygit2.Tree)
    assert str(repo._pg2_tree.id) == 'bfd1938cd1ee3c37b1cc3170c95821deac9ae0ce'
    assert repo.branch == 'master'
    assert os.path.realpath(repo.path) == os.path.realpath(gitrepo)

def test_repository_initialization_bare_branch(gitrepo):
    repo = gitdict.Repository(gitrepo, branch='gh-pages')
    assert str(repo._pg2_tree.id) == 'dfbc8ee7ad6ebb3600c5372e094bfba447b4511d'
    assert repo.branch == 'gh-pages'
    
def test_repository_is_bare_passthrough(gitrepo):
    repo = gitdict.Repository(gitrepo)
    assert repo.is_bare == True
    