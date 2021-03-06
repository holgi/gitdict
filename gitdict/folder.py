''' gitdict.Folder '''

# standard library imports
import os
import collections

# required imports
import pygit2

# imports of gitdict package
from .utils import GitDictError, NodeMixin
from .file import File


class FolderBase(collections.abc.Mapping):
    ''' Base class representating a "git folder" 
    
    The class implements the methods for the abstract base class 'Mapping' for 
    the Repository and Folder classes.
    
    'name' in folder:
        returns true, if a child object is available, else False
    folder['name']  
        retrive child object or raise KeyError
    folder.get('name', default=None)
        retrive child object or return default value
    len(folder)
        the number of child objects
    folder.keys():
        returns an iterator with the names of all child objects
    folder.values()
        returns an iterator with all child objects
    folder.items()
        returns an iterator with tuples of (name, child object) 
    for name in folder
        iterator interface
    something == folder
        compare if something is the same folder
    something != folder
        compare if something is not the same folder
    folder.walk()
        similar to os.walk() returns iterator of tuples 
        (parent_folder, [contained folders], [contained files])
    '''

    def __contains__(self, key):
        ''' Check if a child object exists (collections.abc.Mapping).
        
        key: name of child object
        '''
        try:
            entry = self._pg2_tree[key]
            return entry.type in self.child_map
        except KeyError:
            return False
    
    def get(self, key, default=None):
        ''' Return a child object (collections.abc.Mapping).
        
        key:     name of child object
        default: return value if child object doesn't exist
        '''
        try:
            return self[key]
        except KeyError as error:
            return default
    
    def __getitem__(self, key):
        ''' Return a child object (collections.abc.Mapping).
        
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
            raise KeyError(key)
        return self._child_factory(entry)
    
    def _entries(self):
        ''' Return pygit2.TreeEntries for all child objects.
        
        this will return only tree entries for folders and files
        '''
        return ( e for e in self._pg2_tree if e.type in self.child_map )
    
    def keys(self):
        ''' Names of all child objects (collections.abc.Mapping). '''
        return ( e.name for e in self._entries() )
    
    def items(self):
        ''' Tuples with name and child object (collections.abc.Mapping). '''
        return ( (e.name, self._child_factory(e)) for e in self._entries() )
    
    def values(self):
        ''' All child objects (collections.abc.Mapping). '''
        return ( self._child_factory(e) for e in self._entries() )
    
    def __iter__(self):
        ''' The names of all child objects (collections.abc.Mapping). '''
        return self.keys()
    
    def __len__(self):
        ''' Return number of child objects (collections.abc.Mapping). '''
        return len(list(self._entries()))
    
    def __eq__(self, other):
        ''' Is this equal to another object (collections.abc.Mapping). '''
        if not isinstance(other, FolderBase):
            return False
        return self._pg2_tree.id == other._pg2_tree.id
        
    def __ne__(self, other):
        ''' Is this not equal to another object (collections.abc.Mapping). '''
        if not isinstance(other, FolderBase):
            return True
        return self._pg2_tree.id != other._pg2_tree.id
    
    def walk(self):
        ''' Folder tree generator, similar to os.walk

        For each folder in the folder instance rooted at top (including top
        itself) yields a 3-tuple

            parent folder, contained folders, contained files

        Parent folder is the folder that contains the other parts in the tuple.
        Contained folders is a list of Folders in parent folder.
        Contained filens is a list of Files in parent folder.
        
        In contrast to os.walk, not the git paths are returned but the actual
        File or Folder objects.
        '''
        folders = []
        files = []
        for item in self.values():
            if isinstance(item, Folder):
                folders.append(item)
            else:
                files.append(item)
        yield (self, folders, files)
        for folder in folders:
            yield from folder.walk()


class Folder(FolderBase, NodeMixin):
    ''' Representation of a "git folder" 
    
    Folders should not be initialized directly, but retrieved from a repo: 
        repo = Repository('path/to/repo')
        folder = repository['some_folder']

    From FolderBase:
    'name' in folder:
        returns true, if a child object is available, else False
    folder['name']  
        retrive child object or raise KeyError
    folder.get('name', default=None)
        retrive child object or return default value
    folder.keys():
        returns an iterator with the names of all child objects
    folder.values()
        returns an iterator with all child objects
    folder.values()
        returns an iterator with tuples of (name, child object) 
    len(folder)
        the number of child objects
    for name in folder
        iterator interface
    something == folder
        compare if something is the same folder
    something != folder
        compare if something is not the same folder
    folder.walk()
        similar to os.walk() returns iterator of tuples 
        (parent_folder, [contained folders], [contained files])
    
    From utils.NodeMixin:
    folder.git_path
        path of the object in the git repository
    folder.last_commit
        last commit that affected the folder
    folder.history
        list of commits that affected the folder (newest first)
    
    folder.diff(committish, reference=None)
        pygit2.diff object for the folder compared to the commit
        committish might be a pygit2.Commit or an pygit2.Oid like id
        if reference is also a committish, the diff is between the two commits 
    
    folder.__name__, folder.__parent__: pyramid traversal implementation
    '''
    
    def __init__(self, name, parent, repository, pg2_tree):
        ''' Initialization of the folder.
         
        name:       name of the folder
        parent:     parent folder containing this folder
        repository: the repository
        pg2_tree:   the pygit2 object for this folder
        '''
        self.__name__ = name
        self.__parent__ = parent
        self._repository = repository
        self._pg2_tree = pg2_tree

    def _child_factory(self, tree_entry):
        ''' Create a gitdict object from a pygit2 tree entry '''
        child_class = self.child_map[tree_entry.type]
        pg2_object = self._repository._pg2_repo[tree_entry.id]
        return child_class(tree_entry.name, self, self._repository, pg2_object)
    
    def diff(self, commitish, reference=None):
        ''' Get a pygit2.diff for the same folder in an other commmit.
        
        commitish:  value that refers to a commit
                    might be a pygit2.Commit, a pygit2.Oid or
                    a textual representaion of a pygit2.Oid
                    see utils.ensure_oid()
        reference:  a commit to diff to
                    if reference is None, use previous to last commit
        '''
        pg2_diff_tree = self._get_object_from_commit(commitish)
        if reference is None:
            pg2_ref_tree = self._pg2_tree
        else:
            pg2_ref_tree = self._get_object_from_commit(reference)
        try:
            return pg2_ref_tree.diff_to_tree(pg2_diff_tree)
        except (TypeError, AttributeError):
            # this might happen, if the git path pointed in the requested
            # commit to a tree instead of a blob or a commit does not contain
            # the path requessted
            msg = 'Diff impossible between %s and %s '
            raise GitDictError(msg % (pg2_diff_tree, pg2_ref_tree))
    

# some things have to be added afterwards
FolderBase.child_map = {'tree': Folder, 'blob': File }