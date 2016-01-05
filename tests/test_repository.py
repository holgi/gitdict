import pytest
import os

import pygit2
import gitdict

from . import gitrepo


def example():
    with pytest.raises(Exception):
        assert 1==2
    assert 0

def test_repository_is_also_folder(gitrepo):
    repo = gitdict.Repository(gitrepo)
    assert isinstance(repo, gitdict.FolderBase)

def test_repository_initialization_bare_head(gitrepo):
    repo = gitdict.Repository(gitrepo)
    assert isinstance(repo._pg2_repo, pygit2.Repository)
    assert isinstance(repo.last_commit, pygit2.Commit)
    assert str(repo.last_commit.id) == '7a8474cd44e4aaaa52ad9163d7d1bf971255662f'
    assert isinstance(repo._pg2_tree, pygit2.Tree)
    assert str(repo._pg2_tree.id) == 'bfd1938cd1ee3c37b1cc3170c95821deac9ae0ce'
    assert repo.branch == 'master'
    assert os.path.realpath(repo.path) == os.path.realpath(gitrepo)

def test_repository_initialization_bare_branch(gitrepo):
    repo = gitdict.Repository(gitrepo, branch='gh-pages')
    assert str(repo.last_commit.id) == '19425a1ca1e819f69428edd982d4a8b90d0b9d97'
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
        assert str(repo.last_commit.id) == '7a8474cd44e4aaaa52ad9163d7d1bf971255662f'
        assert str(repo._pg2_tree.id) == 'bfd1938cd1ee3c37b1cc3170c95821deac9ae0ce'

def test_repository_git_path(gitrepo):
    repo = gitdict.Repository(gitrepo)
    assert repo.git_path == ''

def test_repository_branches(gitrepo):
    repo = gitdict.Repository(gitrepo)
    assert repo.branches() == ['gh-pages', 'master', 'merge-commits', 'pr346']

def test_repository_last_commit_for_unknown_path(gitrepo):
    repo = gitdict.Repository(gitrepo)
    with pytest.raises(gitdict.GitDictError):
        repo.last_commit_for('unknown-path')

def test_repository_history(gitrepo):
    repo = gitdict.Repository(gitrepo)
    history = repo.history
    for commit in history:
        assert isinstance(commit, pygit2.Commit)
    assert len(history) == 1242

def test_repository_diff_from_commit(gitrepo):
    repo = gitdict.Repository(gitrepo)
    commit = list(repo.history)[1]
    diff = repo.diff(commit)
    assert isinstance(diff, pygit2.Diff)

def test_repository_diff_raises_error(gitrepo):
    repo = gitdict.Repository(gitrepo)
    with pytest.raises(gitdict.GitDictError):
        assert repo.diff(repo._pg2_tree)