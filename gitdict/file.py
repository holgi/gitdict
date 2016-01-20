''' gitdict.Folder '''

import os
import collections
import io

import pygit2

from .utils import GitDictError, NodeMixin


class File(NodeMixin):
    ''' Simple representation of a "git file" 

    Files should not be initialized directly, but retrieved from a repository: 
        repo = Repository('path/to/repo')
        file = repository['some_file.txt']

    From utils.NodeMixin:
    file.git_path
        path of the object in the git repository
    file.last_commit
        last commit that affected the folder
    file.history
        list of commits that affected the folder (newest first)
    
    file.encoding
        encoding for the file, defaults to repo.default_encoding
    file.data
        binary data of the file content
    file.text
        text content of the file, decoded using file.encoding
    file.decode(encoding=None)
        decode the binary content of the file
        if encoding is None, file.encoding is used
        if encoding is not None, file.encoding is set to encoding 
    file.diff(committish, reference=None)
        pygit2.diff object for the folder compared to the commit
        committish might be a pygit2.Commit or an pygit2.Oid like id
        if reference is also a committish, the diff is between the two commits 

    
    file.__name__, file.__parent__: pyramid traversal implementation
    '''
    
    def __init__(self, name, parent, repository, pg2_blob):
        ''' initialization
        name:       name of the folder
        parent:     parent containing this folder
        repository: the repository
        pg2_blob:   the pygit2 object for this file
        '''
        self.__name__ = name
        self.__parent__ = parent
        self._repository = repository
        self._pg2_blob = pg2_blob
        self.encoding = self._repository.default_encoding
    
    @property
    def data(self):
        ''' access to binary data '''
        return self._pg2_blob.data
    
    @property
    def text(self):
        ''' data as decoded text, uses the currently set encoding '''
        return self.decode()
    
    def decode(self, encoding=None):
        ''' data as decoded text, might use a specified encoding 
        
        if encoding is None, file.encoding is used
        if encoding is not None, file.encoding is set to encoding
        '''
        if encoding:
            self.encoding = encoding
        return self._pg2_blob.data.decode(self.encoding)
    
    def diff(self, commitish, reference=None):
        ''' get a diff for the same file in other commmit(s)
        
        if reference is None, it is the diff to last comitted version
        if reference is not None, the diff between the two commits
        '''
        pg2_diff_blob = self._get_object_from_commit(commitish)
        if reference is None:
            pg2_ref_blob = self._pg2_blob
        else:
            pg2_ref_blob = self._get_object_from_commit(reference)
        try:
            return pg2_ref_blob.diff(pg2_diff_blob)
        except (TypeError, AttributeError):
            # this might happen, if the git path pointed in the requested
            # commit to a tree instead of a blob or a commit does not contain
            # the path requessted
            msg = 'Diff impossible between %s and %s '
            raise GitDictError(msg % (pg2_diff_blob, pg2_ref_blob))
    
    def __iter__(self):
        ''' iterating over lines in a text file 
        
        just like with the standard file object. 
        uses the encoding set in self.encoding 
        (defaults to Repository.default_encoding defaults to utf-8)
        '''
        return io.StringIO(self.text)

