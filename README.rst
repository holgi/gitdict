gitdict – Dict Like Access to a Git Repository
==============================================

The great `pygit2 <http://www.pygit2.org>`__ package enables working with
`python <https://www.python.org>`__ on a `git <http://git-scm.com>`__
repository on a fast but low level basis.

The `gitdict <https://github.com/holgi/gitdict>`__ package builds on
`pygit2 <http://www.pygit2.org>`__ and offers a simple interface to the
git repository, but is currently limited to reading from a repository.

One of the main goals - beside providing a nice git access - is to use
this in a `pyramid <http://www.pylonsproject.org>`__ web application
with a
`traversal <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html>`__
style routing. Of cause, it can also be used otherwise ;-)

The documentation consists mainly of examples.

Introduction by Example
-----------------------

.. code:: python

    # open a Repository
    import gitdict
    repo = Repository('/path/to/gitdict.git')

    # read a folder and a file from the repository
    folder = repo['docs']
    file = folder['index.md']

    # access to file data
    file.data == b'gitdict - Dict Like Access […]'
    file.text == 'gitdict - Dict Like Access […]'
    # iterate over lines in a file, just like with standard python open()
    for line in file:
        do_something(line)

    # data about the last change to the file
    last_change = file.last_commit
    last_change.message == 'latest commit message'
    last_change.author == pygit2.Signature('Holger Frey', 'spam@holgerfrey.de')

    # all changes done to a file
    file.history == [commit_3, commit_2, commit_1]
    # difference between current and a previous version
    patch = file.diff(commit_1)

Overview
--------

There are three main classes in the gitdict package:

-  `Repository <docs/repository.md>`__: used to open a git repository,
   acts also as the 'root folder'
-  `Folder <docs/folder.md>`__: like a folder in the file system,
   located inside a repository
-  `File <docs/file.md>`__: like a file in the file system, stores data
   and is located inside a folder

A ``Folder`` or a ``File`` object should not be created directly but
retrieved either from a ``Repository`` or another ``Folder``.

Some methods just act as a proxy to the underlying pygit2 object, others
do some extra work. In some cases pygit2 object are directly exposed to
the user. But this only happens where simplification is not needed,
IMHO.

Shared Api
----------

This is common in ``Repository``, ``Folder`` and ``File``

-  ``git_path``: path of the object in the git repository
-  ``last_commit``: last commit that introduced a change
-  ``history``: list of commits, that introduced changes, newest first
-  ``diff(commit, reference=None)``: difference between the current object 
    and a previous version, if reference is None, the current commit is used
    to calculate the commit

The ``Repository``, ``Folder`` have a dict-like read-only access to
contained objects in common:

-  ``name in repo_or_folder``: check if a file or folder exists
-  ``repo_or_folder[name]``: retrieve a file or folder, might raise
   KeyError
-  ``repo_or_folder.get(name, default=None)``: retrieve a file or
   folder, or default value
-  ``len(repo_or_folder)``: number of contained files and folders
-  ``repo_or_folder.keys()``: iterator with the name of all contained
   files and folders
-  ``repo_or_folder.values()``: iterator with all contained files and
   folders
-  ``repo_or_folder.items()``: iterator with tuples of (name,
   file\_or\_folder)
-  ``for name in repo_or_folder``: iterator interface
-  ``repo_or_folder.walk()``: similar to os.walk()

Note of Warning
---------------

This package was developed on Mac OS X and `Python
3.5 <https://docs.python.org/3/>`__. There is currently no such thing as
testing on other platforms or Python versions.

If the installation with ``python3 setup.py`` doesn't work, try to
install pygit2 manually first - this is the tricky part. E.g. on my setup 
the cffi-package was missing.

In other words: Works for me ;-)

License?
~~~~~~~~

Well, I decided to go with the `Simplified BSD
License <http://opensource.org/licenses/BSD-2-Clause>`__.

Continue reading
~~~~~~~~~~~~~~~~

-  `Repository <docs/repository.md>`__
-  `Folder <docs/folder.md>`__
-  `File <docs/file.md>`__
