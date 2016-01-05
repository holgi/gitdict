import os
import pygit2


def get_oid(something):
    ''' try to return an pygit2.Oid for an unknown variable type '''
    if isinstance(something, pygit2.Oid):
        return something
    try:
        if isinstance(something, str):
            return pygit2.Oid(hex=commit)
        if isinstance(something, bytes):
            return pygit2.Oid(raw=commit)
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
        
    def diff(self, commit):
        commit_id = get_oid(commit)
        
