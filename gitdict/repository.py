''' gitdict.Repository '''

import pygit2


class Repository(object):
    ''' Simple representation of a git repository and "root folder" '''
    
    def __init__(self, repository_path, branch=None):
        ''' initialization of the repository class 
        
            repository_path: path to git repository to use
            branch:          local git branch to work on. 
                             if no branch is provided, the git head will be used
        '''
        self._pg2_repo = pygit2.Repository(repository_path)
        if branch is None:
            ref = self._pg2_repo.head
        else:
            ref = self._pg2_repo.lookup_branch(branch, pygit2.GIT_BRANCH_LOCAL)
        commit = self._pg2_repo[ref.target]
        self._pg2_tree = commit.tree
        # the shorthand name of the reference is used a branch name
        # this will also point to a branch from git head.
        self.branch = ref.shorthand
        self.path = self._pg2_repo.path
    
    @property
    def is_bare(self):
        ''' is the repository in use a bare repository? '''
        return self._pg2_repo.is_bare