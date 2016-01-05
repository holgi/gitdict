import os
import pygit2


def ensure_oid(something):
    ''' try to return an pygit2.Oid for an unknown variable type '''
    if isinstance(something, pygit2.Oid):
        return something
    try:
        if isinstance(something, str):
            return pygit2.Oid(hex=something)
        if isinstance(something, bytes):
            return pygit2.Oid(raw=something)
        if isinstance(something.id, pygit2.Oid):
            return something.id
    except (ValueError, AttributeError, TypeError):
        pass
    raise GitDictError('Unconvertable Oid: ' + repr(something))


def get_or_none(dict_like, what):
    ''' returns a dict entry or None
    
    Unfortunately, the pygit2.Tree object does not implement a get() method 
    with a default value.
    Mostly used in Repository._commit_touches_path()    
    '''
    try:
        return dict_like[what]
    except KeyError:
        return None
        

class GitDictError(Exception):
    pass


class NodeMixin(object):

    @property
    def git_path(self):
        ''' the path of the git object in the repository '''
        return os.path.join(self.__parent__.git_path, self.__name__)
    
    @property
    def commit(self):
        ''' the commit where the file was last changed '''
        return self._repository.last_commit_for(self.git_path)

    @property
    def history(self):
        ''' commit history of the file '''
        return self._repository.commit_history_for(self.git_path)
        
    def _get_object_from_commit(self, commitish):
        commit_id = ensure_oid(commitish)
        commit = self._repository._pg2_repo[commit_id]
        if not isinstance(commit, pygit2.Commit):
            raise GitDictError('Not a commit: ' + repr(commit))
        path = self.git_path
        entry = get_or_none(commit.tree, path)
        return self._repository._pg2_repo[entry.id] if entry else None

        
        
