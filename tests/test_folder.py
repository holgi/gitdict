import pytest
import os

import pygit2
import gitdict

from . import gitrepo

docs_folder_content = {
    '_static':          gitdict.Folder,
    '_themes':          gitdict.Folder,
    'recipes':          gitdict.Folder,
    'Makefile':         gitdict.File,
    'blame.rst':        gitdict.File,
    'conf.py':          gitdict.File,
    'config.rst':       gitdict.File,
    'development.rst':  gitdict.File,
    'diff.rst':         gitdict.File,
    'features.rst':     gitdict.File,
    'general.rst':      gitdict.File,
    'index.rst':        gitdict.File,
    'install.rst':      gitdict.File,
    'log.rst':          gitdict.File,
    'merge.rst':        gitdict.File,
    'objects.rst':      gitdict.File,
    'oid.rst':          gitdict.File,
    'recipes.rst':      gitdict.File,
    'references.rst':   gitdict.File,
    'remotes.rst':      gitdict.File,
    'repository.rst':   gitdict.File,
    'revparse.rst':     gitdict.File,
    'settings.rst':     gitdict.File,
    'submodule.rst':    gitdict.File,
    'working-copy.rst': gitdict.File }

def example():
    with pytest.raises(Exception):
        assert 1==2
    assert 0

def test_folder_init(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    assert folder.__name__ == 'docs'
    assert folder.__parent__ == repo
    assert folder._repository == repo
    assert isinstance(folder._pg2_tree, pygit2.Tree)
    assert str(folder._pg2_tree.id) == '67336d9821cdb3209177d38a198e20a51eef5cca'

def test_folder_git_path(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']['recipes']
    assert folder.git_path == 'docs/recipes'
    
def test_folder_contains(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    assert 'recipes' in folder
    assert 'Makefile' in folder
    assert 'recipes/git-init.rst' in folder
    assert 'unknown' not in folder

def test_folder_get_folder(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    child = folder.get('recipes')
    assert isinstance(child, gitdict.Folder)
    assert child.__parent__ == folder

def test_folder_get_file(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    child = folder.get('Makefile')
    assert isinstance(child, gitdict.File)
    assert child.__parent__ == folder


def test_folder_get_path(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    child = folder.get('recipes/git-init.rst')
    assert isinstance(child, gitdict.File)
    assert child.__parent__ == folder['recipes']

def test_folder_get_default_on_unknown_child(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    child = folder.get('unknown_child', 'default_value')
    assert not isinstance(child, gitdict.File)
    assert child == 'default_value'

def test_folder_keys(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    assert sorted(folder.keys()) == sorted(docs_folder_content.keys())

def test_folder_items(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    content = docs_folder_content.copy()
    for name, object in folder.items():
        cls = content.pop(name)
        assert isinstance(object, cls)
    assert len(content) == 0

def test_folder_values(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    content = docs_folder_content.copy()
    for object in folder.values():
        cls = content.pop(object.__name__)
        assert isinstance(object, cls)
    assert len(content) == 0

def test_folder_iter(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    names = [name for name in folder]
    assert sorted(names) == sorted(docs_folder_content.keys())
    
def test_folder_len(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    assert len(folder) == 25

def test_fodler_equals(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder1 = repo['docs']
    folder2 = repo['docs']
    assert id(folder1) != id(folder2)
    assert folder1 == folder2
    assert ('x' == folder1) == False

def test_fodler_not_equals(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs']
    assert folder != 'x'
    assert folder != repo
    assert folder != folder['recipes']


def test_commit(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs/recipes']
    commit = folder.commit
    assert isinstance(commit, pygit2.Commit)
    message = commit.message
    assert message.startswith('Fix indent error')
    
def test_history(gitrepo):
    repo = gitdict.Repository(gitrepo)
    folder = repo['docs/recipes']
    expected = [
        'Fix indent error',
        'Add a recipe for git clone --mirror',
        'Cherry-pick recipe: clean up after picking',
        'Add git-cherry-pick recipes',
        'git-show recipe: Add the easy Python 3 way',
        'Clarify comments in git-show recipe',
        'Correct git-show recipe',
        'Update git-show recipe',
        'Remove obsolete git-branch recipe',
        'docs: clarify git-init recipe',
        'docs: adjust to recent changes',
        'Doc fixes: change head.oid to head.target in examples',
        'restructured recipes' ]
    for i, commit in enumerate(folder.history):
        assert isinstance(commit, pygit2.Commit)
        assert commit.message.startswith(expected[i])
    assert len(list(folder.history)) == len(expected)