"""
Utils for fixtures.

@author: schipiga@mirantis.com
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tempfile
import uuid

import attrdict
from six import moves


def generate_ids(prefix=None, postfix=None, count=1, length=None):
    """Generate unique identificators, based on uuid.

    Arguments:
        - prefix: prefix of uniq ids, default is None.
        - postfix: postfix of uniq ids, default is None.
        - count: count of uniq ids, default is 1.
        - length: length of uniq ids, default is not limited.

    Returns:
        - generator of uniq ids.
    """
    for _ in moves.range(count):
        uid = str(uuid.uuid4())
        if prefix:
            uid = '{}-{}'.format(prefix, uid)
        if postfix:
            uid = '{}-{}'.format(uid, postfix)
        if length:
            uid = uid[0:length]
        yield uid


def generate_files(prefix=None, postfix=None, folder=None, count=1, size=1024):
    """Generate files with unique names.

    Arguments:
        - prefix: prefix of uniq ids, default is None.
        - postfix: postfix of uniq ids, default is None.
        - folder: folder to create uniq files.
        - count: count of uniq ids, default is 1.
        - size: size of uniq files, default is 1Mb.

    Returns:
        - generator of files with uniq names.
    """
    folder = folder or tempfile.mkdtemp()
    if not os.path.isdir(folder):
        os.makedirs(folder)

    for uid in generate_ids(prefix, postfix, count):
        file_path = os.path.join(folder, uid)

        with open(file_path, 'wb') as f:
            f.write(os.urandom(size))

        yield file_path


def get_size(value, to):
    """Get size of value with specified type."""
    _map = {'TB': 1024 * 1024 * 1024 * 1024,
            'GB': 1024 * 1024 * 1024,
            'MB': 1024 * 1024,
            'KB': 1024}

    value = value.upper()
    to = to.upper()

    for k, v in _map.items():
        if value.endswith(k):
            value = int(value.strip(k).strip()) * v
            break
    else:
        value = int(value) * 1024

    for k, v in _map.items():
        if to == k:
            return value / v


def slugify(string):
    """Slugify test names to put test results in folder with test name."""
    return ''.join(s if s.isalnum() else '_' for s in string).strip('_')


class AttrDict(attrdict.AttrDict):
    """Wrapper over attrdict to provide context manager to update fields."""

    _updated_fields = {}

    def __init__(self, *args, **kwgs):
        """Constructor."""
        super(AttrDict, self).__init__(*args, **kwgs)

    def put(self, **kwgs):
        """Put fields to update in buffer."""
        self._updated_fields[id(self)] = kwgs
        return self

    def __enter__(self):
        """Enter to context manager."""
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Update fields from buffer on exit from context manager."""
        updated_fields = self._updated_fields.pop(id(self))
        self.update(updated_fields)
