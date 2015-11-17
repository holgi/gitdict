gitdict
=======

Access a git repository like a pyhton dict, based on pygit2.


opening a git repository
------------------------

    # standard way
    repo = gitdict.Repository('path/to/repo')
    
    # as a context manager
    with gitdict.Repository('path/to/repo') as repo:
        # do stuff
    
    # using branches
    branch = gitdict.Repository('path/to/repo', branch='master')


reading from a repository
-------------------------

    first = repo['first_file']
    
    folder = repo['folder_name']
    second = folder['second_file']
    
    third = repo['some/third/file']
    third == repo['some']['third']['file']


writing to a repository
-----------------------

This is a little bit more tricky, since we need to commit our changes:

    author = gitdict.Signature('Author Name', 'Author Email')
    message = 'a really cool change'
    
    # standard way
    repo['changed_text_file'] = 'this has changed so much'
    repo['new_binary_file'] = b'some bytes'
    folder = repo['folder']
    folder['sub_folder/and_file'] = 'will be created'
    del repo['not_needed_anymore']            
    repo.commit(message, author)
    
    # as a context manager
    with repo.prepare_commit(message, author) as commit:
        commit['changed_text_file'] = 'this has changed so much'
        commit['new_binary_file'] = b'some bytes'
        folder = commit['folder']
        folder['sub_folder/and_file'] = 'will be created'
        del commit['not_needed_anymore']            


more ideas
----------
    
    last_commit = repo.last_commit
    last_commit.message == 'a really cool change'
    last_commit.author == gitdict.Signature('Author Name', 'Author Email')
    
    some_file.path == 'somewhere/is/a/file'
    last_commit = file.last_commit
    last_commit.message == 'this only fixed a typo'
    last_commit.author == gitdict.Signature('Author Name', 'Author Email')
    
    some_file.changes == [file_revision_3, file_revision_2, file_revision_1]
    
    some_file.data == b'some binary data'
    some_file.text == some_file.data.decode('utf-8')
    
    
        
    
    
notes to self
-------------

- pygit2.Repository.default_signature: Signatur lt. Repo-Config
- 