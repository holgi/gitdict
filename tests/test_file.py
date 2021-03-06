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

def test_file_get_raw_data(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['.gitattributes']
    assert gf.data == '*.h text eol=lf\n'.encode('utf-8')
    assert isinstance(gf.data, bytes)

def test_file_get_text_default_encoding(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['.gitattributes']
    assert isinstance(gf.text, str)
    assert gf.text == '*.h text eol=lf\n'
    assert gf.decode() == '*.h text eol=lf\n'

def test_file_get_text_specific_encoding(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['.gitattributes']
    assert gf.encoding == 'utf-8'
    assert gf.decode('ascii') == '*.h text eol=lf\n'
    assert gf.encoding == 'ascii'

def test_file_last_commit(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['README.rst']
    commit = gf.last_commit
    assert isinstance(gf.last_commit, pygit2.Commit)
    message = commit.message
    assert message.startswith("Release 0.23.2")
    
def test_file_history(gitrepo):
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

def test_file_diff_from_commit(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['docs/recipes/git-show.rst']
    commit = list(gf.history)[1]
    diff = gf.diff(commit)
    assert isinstance(diff, pygit2.Patch)
    assert diff.line_stats == (15, 9, 2)

def test_file_diff_between_commits(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['docs/recipes/git-show.rst']
    commit1 = list(gf.history)[1]
    commit2 = list(gf.history)[2]
    diff = gf.diff(commit1, commit2)
    assert isinstance(diff, pygit2.Patch)
    assert diff.line_stats == (14, 4, 4)

def test_file_get_object_from_commit_raises_error(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['docs/recipes/git-show.rst']
    with pytest.raises(gitdict.GitDictError):
        assert gf._get_object_from_commit(repo._pg2_tree)

def test_file_iterator(gitrepo):
    repo = gitdict.Repository(gitrepo)
    gf = repo['docs/recipes/git-show.rst']
    lines = [
        '*' * 70,
        'git-show',
        '*' * 70,
        '',
        '-' * 70,
        'Showing a commit',
        '-' * 70,
        '',
        '.. code-block:: bash']
    expected = [l+'\n' for l in lines]
    result = [line for line in gf]
    assert result[:9] == expected