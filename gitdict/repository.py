''' gitdict.Repository '''

import pygit2

from .exceptions import GitDictError


class Repository(object):
    ''' Simple representation of a git repository and "root folder" 
    
    '''
    
    def __init__(self, repository_path, branch=None):
        ''' initialization of the repository class 
        
        repository_path: path to git repository to use
        branch:          local git branch to work on. 
                         if no branch is provided, the git head will be used
        
        raises GitDictError if the repository could not be opened or the branch
        requested is not found.
        '''
        try:
            self._pg2_repo = pygit2.Repository(repository_path)
        except Exception:
            message = 'could not open repository at path ' + repository_path
            raise GitDictError(message)
        if branch is None:
            ref = self._pg2_repo.head
        else:
            ref = self._pg2_repo.lookup_branch(branch, pygit2.GIT_BRANCH_LOCAL)
            if not ref:
                raise GitDictError('could not find local branch ' + branch)
        self.commit = self._pg2_repo[ref.target]
        self._pg2_tree = self.commit.tree
        # the shorthand name of the reference is used as a branch name
        # this will also point to a branch from git head.
        self.branch = ref.shorthand
        self.path = self._pg2_repo.path
    
    @property
    def is_bare(self):
        ''' is the repository in use a bare repository? '''
        return self._pg2_repo.is_bare
    
    # context manager interface
    def __enter__(self):
        ''' context manager interface: enable class as context manager '''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): 
        ''' context manager interface: propagate any exception '''
        return False