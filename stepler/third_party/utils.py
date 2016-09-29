"""
Utils.

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

import email.utils
import logging
import os
import tempfile
import uuid

import requests

from stepler import config
from stepler.third_party.steps_checker import step

LOGGER = logging.getLogger(__name__)


@step
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
    for _ in range(count):
        uid = str(uuid.uuid4())
        if prefix:
            uid = '{}-{}'.format(prefix, uid)
        if postfix:
            uid = '{}-{}'.format(uid, postfix)
        if length:
            uid = uid[0:length]
        yield uid


@step
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
