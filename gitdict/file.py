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
        ''' Initialization of the file.
        
        name:       name of the file
        parent:     parent folder containing this file
        repository: the repository
        pg2_blob:   the pygit2 object for this file
        '''
        self.__name__ = name
        self.__parent__ = parent
        self._repository = repository
        self._pg2_blob = pg2_blob
        # since we probably mostly deal with text files,
        # the encoding ist set to the default encoding set in Repository class
        # that defaults to utf-8
        self.encoding = self._repository.default_encoding
    
    @property
    def data(self):
        ''' Return raw binary file content '''
        return self._pg2_blob.data
    
    @property
    def text(self):
        ''' Return file content as text, uses currently set encoding. '''
        return self.decode()
    
    def decode(self, encoding=None):
        ''' Return Data as decoded text, might use a specified encoding 
        
        encoding:   encoding to be used to decode the text
                    sets also the file.encoding property
                    if None, file.encoding is used
        '''
        if encoding:
            self.encoding = encoding
        return self._pg2_blob.data.decode(self.encoding)
    
    def diff(self, commitish, reference=None):
        ''' Get a diff for the same file in an other commmit
                
        commitish:  value that refers to a commit
                    might be a pygit2.Commit, a pygit2.Oid or
                    a textual representaion of a pygit2.Oid
                    see utils.ensure_oid()
        reference:  a commit to diff to
                    if reference is None, use previous to last commit
        '''
        pg2_diff_blob = self._get_object_from_commit(commitish)
        if reference is None:
            pg2_ref_blob = self._pg2_blob
        else:
            pg2_ref_blob = self._get_object_from_commit(reference)
        try:
            return pg2_diff_blob.diff(pg2_ref_blob)
        except (TypeError, AttributeError):
            # this might happen, if the git path pointed in the requested
            # commit to a tree instead of a blob or a commit does not contain
            # the path requessted
            msg = 'Diff impossible between %s and %s '
            raise GitDictError(msg % (pg2_diff_blob, pg2_ref_blob))
    
    def __iter__(self):
        ''' Iterating over lines in a text file 
        
        just like with the standard file object. 
        uses the encoding set in self.encoding 
        (defaults to Repository.default_encoding defaults to utf-8)
        '''
        return io.StringIO(self.text)

