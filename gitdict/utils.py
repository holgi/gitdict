import os
import pygit2


def ensure_oid(something):
    ''' Return an pygit2.Oid for an unknown variable type.
    
    something:  a representation of a pygit2.Oid
    
    Raises a GitDictError, if conversion fails
    '''
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


def dict_like_get(dict_like, key, default=None):
    ''' Return a dict entry or None.
    
    Unfortunately, the pygit2.Tree object does not implement a get() method 
    with a default value.
    
    key:    the key to query the pygit2.Tree
    defaut: default value to return, if the key is not found
    
    Mostly used in Repository._commit_touches_path()    
    '''
    try:
        return dict_like[key]
    except KeyError:
        return default
        

class GitDictError(Exception):
    ''' Exception used in gitdict package. '''
    pass


class NodeMixin(object):
    ''' Methods shared between Folder and File classes.
     
    The Repository class uses the same interface, but has a different 
    implementation.
    
    file_or_folder.git_path
        path of the object in the git repository
    file_or_folder.last_commit
        last commit that affected the file or folder
    file_or_folder.history
        list of commits that affected the file or folder (newest first)
    '''

    @property
    def git_path(self):
        ''' Return the path of the git object in the repository. '''
        return os.path.join(self.__parent__.git_path, self.__name__)
    
    @property
    def last_commit(self):
        ''' Return the commit that introduced the last change. '''
        return self._repository.last_commit_for(self.git_path)

    @property
    def history(self):
        ''' Retrun a list of commits that affected the object, newest first. '''
        
        return self._repository.commit_history_for(self.git_path)
        
    def _get_object_from_commit(self, commitish):
        ''' Retrieve an object with the same git path from an other commit. 
        
        commititsh: an commit like object
                    e.g. string representation of a pygit2.Oid
                    
        Raises an GitDictError, if the commitish does not represent a commit.
        '''
        commit_id = ensure_oid(commitish)
        commit = self._repository._pg2_repo[commit_id]
        if not isinstance(commit, pygit2.Commit):
            raise GitDictError('Not a commit: ' + repr(commit))
        entry = dict_like_get(commit.tree, self.git_path)
        return self._repository._pg2_repo[entry.id] if entry else None

        
        
