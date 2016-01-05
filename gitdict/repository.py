''' gitdict.Repository '''

import pygit2

from .utils import GitDictError, get_or_none, ensure_oid
from .folder import FolderBase

class Repository(FolderBase):
    ''' Simple representation of a git repository and "root folder" 
    
    '''
    
    __name__   = None
    __parent__ = None
    
    default_encoding = 'utf-8'
    
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
        self.last_commit = self._pg2_repo[ref.target]
        self._pg2_tree = self.last_commit.tree
        # the shorthand name of the reference is used as a branch name
        # this will also point to a branch from git head.
        self.branch = ref.shorthand
        self.path = self._pg2_repo.path
    
    def branches(self):
        ''' list all local branches in the git repository '''
        flag = pygit2.GIT_BRANCH_LOCAL
        return [branch for branch in self._pg2_repo.listall_branches(flag)]
    
    def last_commit_for(self, git_path):
        ''' searches the latest commit for a given git path '''
        history = list(self.commit_history_for(git_path))
        if len(history) > 0:
            return history[0]
        raise GitDictError('No commit for: ' + git_path)
    
    def commit_history_for(self, git_path):
        ''' history of all commits and ids for a given git path 
        
        with a lot of help from https://github.com/gollum/rugged_adapter/
        '''
        sorting = pygit2.GIT_SORT_TIME | pygit2.GIT_SORT_REVERSE
        history = []
        walker = self._pg2_repo.walk(self.last_commit.id, sorting)
        for commit in walker:
            if len(commit.parents) > 1:
                continue
            if self._commit_touches_path(commit, git_path, walker):
                history.append(commit)
        return reversed(history)

    def _commit_touches_path(self, commit, git_path, walker):
        ''' returns true if a commit introduced changes to a path
        
        Uses commit trees to make that determination. This mimics the 
        history simplification rules that `git log` uses by default, where 
        a commit is omitted if it is TREESAME to any parent.
        
        with a lot of help from https://github.com/gollum/rugged_adapter/
        '''
        entry = get_or_none(commit.tree, git_path)
        if not commit.parents:
            # This is the root commit, return true if it has path in its tree
            return True if entry else False
        treesame = False
        for parent in commit.parents:
            parent_entry = get_or_none(parent.tree, git_path)
            # Only follow the first TREESAME parent for merge commits
            if treesame:
                walker.hide(parent.id)
                walker.next()
            if entry is None and parent_entry is None:
                treesame = True
            elif entry and parent_entry and entry.id == parent_entry.id:
                treesame = True
        return not treesame
        
    def diff(self, commitish):
        ''' get a diff for an other commmit '''
        commit_id = ensure_oid(commitish)
        commit = self._pg2_repo[commit_id]
        if not isinstance(commit, pygit2.Commit):
            raise GitDictError('Not a commit: ' + repr(commit))
        return self._pg2_tree.diff_to_tree(commit.tree)
    
    @property
    def history(self):
        ''' history of all commits and ids for the repository '''
        sorting = pygit2.GIT_SORT_TOPOLOGICAL
        history = []
        for commit in self._pg2_repo.walk(self.last_commit.id, sorting):
            history.append(commit)
        return history
    
    @property
    def git_path(self):
        ''' the path of the git object in the repository '''
        return ''
        
    @property
    def is_bare(self):
        ''' is the repository in use a bare repository? '''
        return self._pg2_repo.is_bare
    
    def _child_factory(self, tree_entry):
        ''' create a gitdict object from a pygit2 tree entry '''
        child_class = self.child_map[tree_entry.type]
        pg2_object = self._pg2_repo[tree_entry.id]
        return child_class(tree_entry.name, self, self, pg2_object)

    # context manager interface
    def __enter__(self):
        ''' context manager interface: enable class as context manager '''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): 
        ''' context manager interface: propagate any exception '''
        return False