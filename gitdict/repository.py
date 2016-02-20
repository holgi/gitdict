''' gitdict.Repository '''

import pygit2

from .utils import GitDictError, dict_like_get , ensure_oid
from .folder import FolderBase

class Repository(FolderBase):
    ''' Simple representation of a git repository and "root folder" 
    
    Example:
        repo = Repository('path/to/repo')
        file = Repository['some_file.txt']
        folder = Repository['some_folder']
    
    These methods have a different implemetation from the ones in the 
    Folder class.
    
    derived from FolderBase:
    'name' in repo:
        returns true, if a child object is available, else False
    repo['name']  
        retrive child object or raise KeyError
    repo.get('name', default=None)
        retrive child object or return default value
    repo.keys():
        returns an iterator with the names of all child objects
    repo.values()
        returns an iterator with all child objects
    repo.values()
        returns an iterator with tuples of (name, child object) 
    len(repo)
        the number of child objects
    for name in repo
        iterator interface
    something == repo
        compare if something is the same folder
    something != repo
        compare if something is not the same folder
    repo.walk()
        similar to os.walk() returns iterator of tuples 
        (parent_folder, [contained folders], [contained files])
    
    interface like utils.NodeMixin:
    repo.git_path
        path of the object in the git repository
    repo.last_commit
        last commit that affected the folder
    repo.history
        list of commits that affected the folder (newest first)
    
    repo.is_bare
        check if this is a bare repository
    repo.path
        path to the repository
    repo.branch
        branch name that was opened
    repo.branches
        list all local branches in the git repository
    repo.default_encoding
        default encoding for text files
    repo.last_commit_for(git_path):
        last commit that affected the node located at git_path
    repo.commit_history_for(git_path)
        all commits that affected the node located at git_path
    repo.diff(committish, reference=None)
        pygit2.diff object for the folder compared to the commit
        committish might be a pygit2.Commit or an pygit2.Oid like id
        if reference is also a committish, the diff is between the two commits 
    
    with repo as r:
        syntactic sugar, context manager interface
    
    repo.__name__, repo.__parent__: pyramid traversal implementation
    '''
    
    __name__   = None
    __parent__ = None
    
    default_encoding = 'utf-8'
    
    def __init__(self, repository_path, branch=None):
        ''' Initialization of the repository class 
        
        repository_path: path to git repository to use
        branch:          local git branch to work on 
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
    
    # interface like utils.NodeMixin
    @property
    def history(self):
        ''' Retrun a list of commits in the repository, newest first. '''
        sorting = pygit2.GIT_SORT_TOPOLOGICAL
        history = []
        for commit in self._pg2_repo.walk(self.last_commit.id, sorting):
            history.append(commit)
        return history
    
    @property
    def git_path(self):
        ''' Return the path for the root folder in the repository. 
        
        This just returns an empty string. 
        The NodeMixin.git_path() implementation relies on this.
        '''
        return ''
        
    @property
    def is_bare(self):
        ''' Check if the repository in use is a bare repository. '''
        return self._pg2_repo.is_bare
    
    @property
    def branches(self):
        ''' List all local branches in the git repository. '''
        flag = pygit2.GIT_BRANCH_LOCAL
        return [branch for branch in self._pg2_repo.listall_branches(flag)]
    
    def last_commit_for(self, git_path):
        ''' Search the latest commit for a given git path in the repository. '''
        try:
            history = self.commit_history_for(git_path)
            return history.__next__()
        except StopIteration:
            raise GitDictError('No commit for: ' + git_path)
    
    def commit_history_for(self, git_path):
        ''' Retrun a list of commits that affected the git path.
        
        The list is in reverse chronological order.
        
        git_path:   path in the git repository to return the history for
        
        With a lot of help from https://github.com/gollum/rugged_adapter/
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
        ''' Check if a commit introduced changes to a path.
        
        Uses commit trees to make that determination. This mimics the 
        history simplification rules that `git log` uses by default, where 
        a commit is omitted if it is TREESAME to any parent.
        
        commit:   the commit that might have introduced a change
        git_path: the path in the git repository to check
        walker:   pygit2 object for iterating through the repository
        
        With a lot of help from https://github.com/gollum/rugged_adapter/
        '''
        entry = dict_like_get(commit.tree, git_path)
        if not commit.parents:
            # This is the root commit, return true if it has path in its tree
            return True if entry else False
        treesame = False
        for parent in commit.parents:
            parent_entry =  dict_like_get(parent.tree, git_path)
            # Only follow the first TREESAME parent for merge commits
            if treesame:
                walker.hide(parent.id)
                walker.next()
            if entry is None and parent_entry is None:
                treesame = True
            elif entry and parent_entry and entry.id == parent_entry.id:
                treesame = True
        return not treesame
    
    def diff(self, commitish, reference=None):
        ''' Get a pygit2.diff for the root folder in an other commmit.
        
        commitish:  value that refers to a commit
                    might be a pygit2.Commit, a pygit2.Oid or
                    a textual representaion of a pygit2.Oid
                    see utils.ensure_oid()
        reference:  a commit to diff to
                    if reference is None, use previous to last commit
        '''
        commit_id = ensure_oid(commitish)
        commit = self._pg2_repo[commit_id]
        if reference is None:
            pg2_ref_commit = self.last_commit
        else:
            reference_id = ensure_oid(reference)
            pg2_ref_commit = self._pg2_repo[reference_id]
        try:
            return pg2_ref_commit.tree.diff_to_tree(commit.tree)
        except (TypeError, AttributeError):
            # this might happen, either commitish or reference do not point
            # to a commit
            msg = 'Diff impossible between %s and %s '
            raise GitDictError(msg % (commit, pg2_ref_commit))
            
    def _child_factory(self, tree_entry):
        ''' Create a gitdict object from a pygit2 tree entry. '''
        child_class = self.child_map[tree_entry.type]
        pg2_object = self._pg2_repo[tree_entry.id]
        return child_class(tree_entry.name, self, self, pg2_object)

    # context manager interface
    def __enter__(self):
        ''' Context manager interface: Enable class as context manager. '''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): 
        ''' Context manager interface: Propagate any exception. '''
        return False