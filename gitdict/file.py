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