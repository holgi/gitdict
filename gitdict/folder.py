''' gitdict.Folder '''

import os
import collections

import pygit2

from .exceptions import GitDictError
from .file import File


class FolderBase(collections.abc.Mapping):
    ''' Base class representating a "git folder" 
    
    These methods are used in the Repository and Folder classes.
    '''

    def __contains__(self, key):
        ''' check if a child object exists (collections.abc.Mapping)
        key: name of child object
        '''
        try:
            entry = self._pg2_tree[key]
            return entry.type in self.child_map
        except KeyError:
            return False
    
    def get(self, key, default=None):
        ''' return a child object (collections.abc.Mapping)
        key: name of child object
        default: return value if child object doesn't exist
        raises KeyError, if the child object doesn't exist and default is None
        '''
        try:
            return self[key]
        except KeyError as error:
            if default is not None:
                return default
            raise error
    
    def __getitem__(self, key):
        ''' return a child object (collections.abc.Mapping)
        key: name of child object
        raises KeyError, if the child object doesn't exist
        '''
        # also a path might be requested
        # in order to get the right "chain", we need to spit the path up, 
        # get only the current child and pass the rest of the path along
        if os.path.sep in key:
            child_name, rest = key.split(os.path.sep, 1)
            child = self[child_name]
            return child[rest]
        # a direct child element was requested
        entry = self._pg2_tree[key]
        if not entry.type in self.child_map:
            raise KeyError( "'{}'".format(key) )
        return self._child_factory(entry)
    
    def _entries(self):
        ''' pygit2 Tree Entries for all child objects '''
        return ( e for e in self._pg2_tree if e.type in self.child_map )
    
    def keys(self):
        ''' The names of all child objects (collections.abc.Mapping) '''
        return ( e.name for e in self._entries() )
    
    def items(self):
        ''' Tuples with name and child object (collections.abc.Mapping) '''
        return ( (e.name, self._child_factory(e)) for e in self._entries() )
    
    def values(self):
        ''' All child objects (collections.abc.Mapping) '''
        return ( self._child_factory(e) for e in self._entries() )
    
    def __iter__(self):
        ''' The names of all child objects (collections.abc.Mapping) '''
        return self.keys()
    
    def __len__(self):
        ''' number of child objects (collections.abc.Mapping) '''
        return len(list(self._entries()))
    
    def __eq__(self, other):
        ''' is this equal to another object (collections.abc.Mapping) '''
        if not isinstance(other, FolderBase):
            return False
        return self._pg2_tree.id == other._pg2_tree.id
        
    def __ne__(self, other):
        ''' is this not equal to another object (collections.abc.Mapping) '''
        if not isinstance(other, FolderBase):
            return True
        print('x')
        return self._pg2_tree.id != other._pg2_tree.id


class Folder(FolderBase):
    ''' Representation of a "git folder" 
    
    These methods are different from the one in the Repository class.
    '''
    
    def __init__(self, name, parent, repository, pg2_tree):
        ''' initialization
        name:       name of the folder
        parent:     parent containing this folder
        repository: the repository
        pg2_tree:   the pygit2 object for this folder
        '''
        self.__name__ = name
        self.__parent__ = parent
        self._repository = repository
        self._pg2_tree = pg2_tree

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


    def _child_factory(self, tree_entry):
        ''' create a gitdict object from a pygit2 tree entry '''
        child_class = self.child_map[tree_entry.type]
        pg2_object = self._repository._pg2_repo[tree_entry.id]
        return child_class(tree_entry.name, self, self._repository, pg2_object)
    

# some things have to be added afterwards
FolderBase.child_map = {'tree': Folder, 'blob': File }