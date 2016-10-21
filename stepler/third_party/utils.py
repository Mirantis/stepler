"""
-----
Utils
-----
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

import email.utils
import inspect
import logging
import os
import tempfile
import uuid

import requests
import six

from stepler import config

if six.PY3:
    basestring = str

LOGGER = logging.getLogger(__name__)

__all__ = [
    'generate_ids',
    'generate_files',
    'get_file_path',
    'get_unwrapped_func',
    'is_iterable',
]


def generate_ids(prefix=None, postfix=None, count=1, length=None):
    """Generate unique identificators, based on UUID.

    Arguments:
        - prefix (string|None): prefix of unique ids.
        - postfix (string|None): postfix of unique ids.
        - count (int|1): count of unique ids.
        - length (int|None): length of unique ids.

    Returns:
        - generator of unique ids.
    """
    for _ in range(count):
        uid = str(uuid.uuid4())
        if prefix:
            # mix constant stepler prefix to separate tested objects
            uid = '{}-{}-{}'.format(config.STEPLER_PREFIX, prefix, uid)
        if postfix:
            uid = '{}-{}'.format(uid, postfix)
        if length:
            uid = uid[0:length]
        yield uid


def generate_files(prefix=None, postfix=None, folder=None, count=1, size=1024):
    """Generate files with unique names.

    Arguments:
        - prefix: prefix of unique ids, default is None.
        - postfix: postfix of unique ids, default is None.
        - folder: folder to create unique files.
        - count: count of unique ids, default is 1.
        - size: size of unique files, default is 1Mb.

    Returns:
        - generator of files with unique names.
    """
    folder = folder or tempfile.mkdtemp()
    if not os.path.isdir(folder):
        os.makedirs(folder)

    for uid in generate_ids(prefix, postfix, count):
        file_path = os.path.join(folder, uid)

        with open(file_path, 'wb') as f:
            f.write(os.urandom(size))

        yield file_path


# TODO(schipiga): copied from mos-integration-tests, need refactor.
def get_file_path(url, name=None):
    """Download file by url to local cached storage."""
    def _get_file_name(url):
        keepcharacters = (' ', '.', '_', '-')
        name = url.rsplit('/')[-1]
        return "".join(c for c in name
                       if c.isalnum() or c in keepcharacters).rstrip()

    if os.path.isfile(url):
        return url

    if not os.path.exists(config.TEST_IMAGE_PATH):
        try:
            os.makedirs(config.TEST_IMAGE_PATH)
        except Exception as e:
            LOGGER.warning("Can't make dir for files: {}".format(e))
            return None

    file_path = os.path.join(config.TEST_IMAGE_PATH, _get_file_name(url))
    headers = {}
    if os.path.exists(file_path):
        file_date = os.path.getmtime(file_path)
        headers['If-Modified-Since'] = email.utils.formatdate(file_date,
                                                              usegmt=True)

    response = requests.get(url, stream=True, headers=headers)

    if response.status_code == 304:
        LOGGER.info("Image file is up to date")
    elif response.status_code == 200:
        LOGGER.info("Start downloading image")
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(65536):
                f.write(chunk)
        LOGGER.info("Image downloaded")
    else:
        LOGGER.warning("Can't get fresh image. HTTP status code is "
                       "{0.status_code}".format(response))

    response.close()
    return file_path


def get_unwrapped_func(func):
    """Get original function under decorator.

    Decorator hides original function inside itself. But in some cases it's
    important to get access to original function, for ex: for documentation.

    Args:
        func (function): function that can be potentially a decorator which
            hides original function

    Returns:
        function: unwrapped function or the same function
    """
    if not inspect.isfunction(func) and not inspect.ismethod(func):
        return func

    if func.__name__ != func.func_code.co_name:
        for cell in func.func_closure:
            obj = cell.cell_contents
            if inspect.isfunction(obj):
                if func.__name__ == obj.func_code.co_name:
                    return obj
                else:
                    return get_unwrapped_func(obj)
    return func


def is_iterable(obj):
    """Define whether object is iterable or no (skip strings).

    Args:
        obj (object): obj to define whether it's iterable or no

    Returns:
        bool: True or False
    """
    if isinstance(obj, basestring):
        return False

    try:
        iter(obj)
        return True

    except TypeError:
        return False
