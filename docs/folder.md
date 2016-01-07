gitdict – Folder
================

In the [gitdict][] package, the `Folder` class is similar to a folder in the file system as it contains other folders or [files][gd_file]. The api is almost the same as in the [`Repository`][gd_repo] class.


Retrieving single Folders and Files
-----------------------------------

In this regard, the `Folder` has the same interface as the [`Repository`][gd_repo] class. This API is derived from the [abstract base class][abc] for unmutable mappings and therfore provides a [dict][] like read-only access to child objects.

```python
import gitdict
repo = gitdict.Repository('path/to/git/repo.git')
folder = repo['docs']

# check if a child object exists
if 'name' in folder:
    pass

# retrive a child object or raise KeyError
folder = file['readme.md']

# retrive a child object or 
# return another  value if it doesn't exist, defaults to None
file = folder.get('readme.md', default=None)

# go some levels deep
sub_folder = folder['sub_folder'] 
file = sub_folder['file_in_sub_folder.txt']

# you can also use paths 
file = folder['sub_folder/file_in_sub_folder.txt']
sub_folder.git_path == 'folder/sub_folder'
```

Work with all contained objects
-------------------------------

```python
# how many child objects are there?
number_of_childs = len(folder)

# iterators of different kinds
names = folder.keys()     # names of all child objects
objects = folder.values() # all child objects
items = folder.items()    # tuples of (name, child object)

# these two are the same
for folder in folder:
    pass
for folder in folder.keys():
    pass

# use a folder just like os.walk, returns iterator of tuples 
# (parent_folder, [contained folders], [contained files])
for parent_folder, contained_folders, contained_files in folder.walk()
    pass
```

Getting information about changes
---------------------------------

```python
# last commmit that introduced a change
commit = folder.last_commit

# this is a pygit2.Commit object
commit.message == 'commit message'
commit.committer.name = 'Holger Frey'
commit.committer.email = 'spam@holgerfrey.de'

# list all commits that introduced changes
# newest commit is listed first
commit_history = folder.history

# get the introduced changes form a commit
# returns a pygit2.Diff object
diff = folder.diff(commit_history[-1])
# you could also use a commit id
diff = folder.diff('34ab790c56d37b34570d2a26a1f9c803e72003c3')
```

### Continue reading

- [Overview][gitdict]
- [Repository][gd_repo]
- [File][gd_file]


[git]:       http://git-scm.com
[abc]:       https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping
[dict]:      https://docs.python.org/3.5/library/stdtypes.html#mapping-types-dict
[gitdict]:   http://example.com
[gd_repo]:   repository.md
[gd_folder]: folder.md
[gd_file]:   file.md