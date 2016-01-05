import os
import pygit2

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
    