import os
import tarfile
import tempfile

import pytest


@pytest.fixture()
def gitrepo(request):
    own_path = os.path.dirname(__file__)
    tar_path = os.path.join(own_path, 'pygit.git.tar.gz')
    tar_file = tarfile.open(tar_path)
    temp_dir = tempfile.TemporaryDirectory()
    request.addfinalizer(temp_dir.cleanup)
    tar_file.extractall(temp_dir.name)
    return temp_dir.name

    