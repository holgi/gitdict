''' gitdict.Folder '''

import os
import collections

import pygit2

from .utils import GitDictError, NodeMixin


class File(NodeMixin):
    ''' Simple representation of a "git file" '''
    
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
        ''' data as decoded text, uses default encoding '''
        return self.decode()
    
    def decode(self, encoding=None):
        ''' data as decoded text, might use a specified encoding '''
        if encoding:
            self.encoding = encoding
        return self._pg2_blob.data.decode(self.encoding)
    
    def diff(self, commitish):
        ''' get a diff for the same file in an other commmit '''
        pg2_object = self._get_object_from_commit(commitish)
        if pg2_object and not isinstance(pg2_object, pygit2.Blob):
            # this might only happen, if the git path pointed in this commit
            # to a tree instead of a blob
            raise GitDictError('Diff impossible for: ' + repr(pg2_object))
        return self._pg2_blob.diff(pg2_object)
