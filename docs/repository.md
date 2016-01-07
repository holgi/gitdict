gitdict – Repository
====================

A repository is the data structure, where [git][] stores the data and history of all files under version controll.

In the [gitdict][] package, the `Repository` class represents such a storage and acts like the 'root folder'. Therfore some of the api is the same as in the [`Folder`][gd_folder] class.

I tried to keep the API consistent accross the `Repository`, `Folder` and `File` class wherever possible.

Opening a Repository
--------------------

```
import gitdict
repo = gitdict.Repository('path/to/repository')

# the same, with some syntactic sugar
with gitdict.Repository('path/to/repository') as repo:
    # work with the repo object
    
# where is the repo located?
file_path = repo.path

# is it a bare repository?
if repo.is_bare:
    pass
```

Working with branches
---------------------

If no branch is spezified when opening a repository, HEAD is used.

```
# opening a branch of a repository
import gitdict
repo = gitdict.Repository('path/to/repository', branch='branch-name')

# getting the currently opened branch name
branch_name = repo.branch

# listing all available local branches
branches = repo.branches
```


Retrieving single Folders and Files
-----------------------------------

In this regard, the `Repository` has the same interface as the [`Folder`][gd_folder] class. This API is derived from the [abstract base class][abc] for unmutable mappings and therfore provides a [dict][] like read-only access to child objects.

```
# check if a child object exists
if 'name' in repo:
    pass

# retrive a child object or raise KeyError
file = repo['readme.md']

# retrive a child object or 
# return another  value if it doesn't exist, defaults to None
file = repo.get('readme.md', default=None)

# go some levels deep
folder = repo['folder'] 
file = folder['file_in_folder.txt']

# you can also use paths 
file = repo['some/path/inside/git/repo.txt']

```

Work with all contained objects
-------------------------------

```
# how many child objects are there?
number_of_childs = len(repo)

# iterators of different kinds
names = repo.keys()     # names of all child objects
objects = repo.values() # all child objects
items = repo.items()    # tuples of (name, child object)

# these two are the same
for name in repo:
    pass
for name in repo.keys():
    pass

# use a repo just like os.walk, returns iterator of tuples 
# (parent_folder, [contained folders], [contained files])
for parent_folder, contained_folders, contained_files in repo.walk()
    pass
```

Getting information about changes
---------------------------------

```
# last commmit that introduced a change
commit = repo.last_commit

# this is a pygit2.Commit object
commit.message == 'commit message'
commit.committer.name = 'Holger Frey'
commit.committer.email = 'spam@holgerfrey.de'

# list all commits that introduced changes
# newest commit is listed first
commit_history = repo.history

# get the introduced changes form a commit
# returns a pygit2.Diff object
diff = repo.diff(commit_history[-1])
# you could also use a commit id
diff = repo.diff('34ab790c56d37b34570d2a26a1f9c803e72003c3')

# interested in a object at a specific path?
commit_for_object = repo.last_commit_for('some/git/path.txt')
history_for_object = repo.commit_history_for('some/git/path.txt') 
```

### Continue reading

- [Overview][gitdict]
- [Folder][gd_folder]
- [File][gd_file]


[git]:       http://git-scm.com
[abc]:       https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping
[dict]:      https://docs.python.org/3.5/library/stdtypes.html#mapping-types-dict
[gitdict]:   http://example.com
[gd_repo]:   repository.md
[gd_folder]: folder.md
[gd_file]:   file.md