gitdict – File
==============

In the [gitdict][] package, the `File` class is like a 'file' in the classical file system – it is an object that contains data, but not other objects.


Getting a File
--------------

```python
import gitdict
repo = gitdict.Repository('path/to/repository')

file = repo['docs']['readme.txt']
file.git_path == 'docs/readme.txt'
```

Working with File Data
----------------------

```python
# getting the (raw) binary data
binary_data = file.data

# since mostly text files are stored, 
# there are some convenient methods

# defaults to repo.defaul_encoding that defaults to 'utf-8'
file.encoding = 'utf-8' 

# uses file.encoding
data_as_text = file.text 

# sets specific file.enconding and decodes with the encoding
text_specific_encoding = file.decode('utf-16') 
# is the same as
file.encoding = 'utf-16'
text_specific_encoding = file.text 
text_specific_encoding == file.decode() 
```

Getting information about changes
---------------------------------

```python
# last commmit that introduced a change
commit = file.last_commit

# this is a pygit2.Commit object
commit.message == 'commit message'
commit.committer.name = 'Holger Frey'
commit.committer.email = 'spam@holgerfrey.de'

# list all commits that introduced changes
# newest commit is listed first
commit_history = file.history

# get the introduced changes form a commit
# returns a pygit2.Patch object
diff = file.diff(commit_history[-1])
# you could also use a commit id
diff = file.diff('34ab790c56d37b34570d2a26a1f9c803e72003c3')
```

### Continue reading

- [Overview][gitdict]
- [Repository][gd_repo]
- [Folder][gd_folder]


[git]:       http://git-scm.com
[abc]:       https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping
[gitdict]:   https://github.com/holgi/gitdict
[gd_repo]:   repository.md
[gd_folder]: folder.md
[gd_file]:   file.md