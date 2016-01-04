''' gitdict.Folder '''

import os
import collections

import pygit2

from .exceptions import GitDictError


class File(object):
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