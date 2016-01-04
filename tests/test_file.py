import pytest
import os

import pygit2
import gitdict

from . import gitrepo


def example():
    with pytest.raises(Exception):
        assert 1==2
    assert 0

def test_file_init(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['README.rst']
    assert gf.__name__ == 'README.rst'
    assert gf.__parent__ == repo
    assert gf._repository == repo
    assert isinstance(gf._pg2_blob, pygit2.Blob)
    assert str(gf._pg2_blob.id) == '4bdf2944e2188cdb8427749317c147239dc212c7'

def test_file_git_path(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['docs']['recipes']['git-init.rst']
    assert gf.git_path == 'docs/recipes/git-init.rst'

def test_get_raw_data(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['.gitattributes']
    assert gf.data == '*.h text eol=lf\n'.encode('utf-8')
    assert isinstance(gf.data, bytes)

def test_get_text_default_encoding(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['.gitattributes']
    assert isinstance(gf.text, str)
    assert gf.text == '*.h text eol=lf\n'
    assert gf.decode() == '*.h text eol=lf\n'

def test_get_text_specific_encoding(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['.gitattributes']
    assert gf.encoding == 'utf-8'
    assert gf.decode('ascii') == '*.h text eol=lf\n'
    assert gf.encoding == 'ascii'

def test_commit(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['README.rst']
    commit = gf.commit
    assert isinstance(gf.commit, pygit2.Commit)
    message = commit.message
    assert message.startswith("Release 0.23.2")
    
def test_history(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['docs/recipes/git-show.rst']
    expected = [
        'git-show recipe: Add the easy Python 3 way',
        'Clarify comments in git-show recipe',
        'Correct git-show recipe',
        'Update git-show recipe',
        'restructured recipes' ]
    for i, commit in enumerate(gf.history):
        assert isinstance(commit, pygit2.Commit)
        assert commit.message.startswith(expected[i])
    assert len(expected) == len(list(gf.history))
