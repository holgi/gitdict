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
    assert isinstance(repo.commit, pygit2.Commit)
    assert str(repo.commit.id) == '7a8474cd44e4aaaa52ad9163d7d1bf971255662f'
    assert isinstance(repo._pg2_tree, pygit2.Tree)
    assert str(repo._pg2_tree.id) == 'bfd1938cd1ee3c37b1cc3170c95821deac9ae0ce'
    assert repo.branch == 'master'
    assert os.path.realpath(repo.path) == os.path.realpath(gitrepo)

def test_repository_initialization_bare_branch(gitrepo):
    repo = gitdict.Repository(gitrepo, branch='gh-pages')
    assert str(repo.commit.id) == '19425a1ca1e819f69428edd982d4a8b90d0b9d97'
    assert str(repo._pg2_tree.id) == 'dfbc8ee7ad6ebb3600c5372e094bfba447b4511d'
    assert repo.branch == 'gh-pages'

def test_repository_error_on_wrong_path(gitrepo):
    no = os.path.join(gitrepo, 'wrongpath')
    with pytest.raises(gitdict.GitDictError):
        repo = gitdict.Repository(no)

def test_repository_error_on_unknown_branch(gitrepo):
    with pytest.raises(gitdict.GitDictError):
        repo = gitdict.Repository(gitrepo, branch='some-unknown-branch')
    
def test_repository_is_bare_passthrough(gitrepo):
    repo = gitdict.Repository(gitrepo)
    assert repo.is_bare == True

def test_repository_as_context_manager(gitrepo):
    with gitdict.Repository(gitrepo) as repo:
        assert str(repo.commit.id) == '7a8474cd44e4aaaa52ad9163d7d1bf971255662f'
        assert str(repo._pg2_tree.id) == 'bfd1938cd1ee3c37b1cc3170c95821deac9ae0ce'
