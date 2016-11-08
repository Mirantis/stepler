"""
---------------------
Glance CLI client steps
---------------------
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

import hashlib
import os
import os.path
import tempfile

from hamcrest import assert_that
from hamcrest import empty
from hamcrest import is_

from stepler.third_party import steps_checker

from .base import BaseCliSteps


class CliGlanceSteps(BaseCliSteps):
    """CLI glance client steps."""

    @steps_checker.step
    def create_file(self, size=0):
        """Step to create file.

        Args:
            size (int): file size in MB
        """
        temp = tempfile.NamedTemporaryFile()
        temp.write(os.urandom(size * 1024))
        temp.close()
        return temp.name

    @steps_checker.step
    def get_image_id(self, name):
        """Step to create image.
        """
        cmd = ("glance image-create --name Test --container-format bare "
               "--disk-format qcow2 --file {0} | "
               "grep id |awk ' {print $4} ' ").format(name)
        result = self.execute_command(cmd)
        return result

    @steps_checker.step
    def download_image(self, uploaded_image_id, downloaded_image_name):
        """Step to download image.
        """
        cmd = 'glance image-download {0} > {1}'.format(
            uploaded_image_id, downloaded_image_name)
        result = self.execute_command(cmd)
        return result

    @steps_checker.step
    def md5_sum(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @steps_checker.step
    def delete_image(self, image_id, check=True):
        """Step to delete image.
        """
        cmd = 'glance image-delete {}'.format(image_id)
        result = self.execute_command(cmd, check=check)
        if check:
            assert_that(result, is_(empty()))

    @steps_checker.step
    def delete_file(self, name_file):
        """Step to delete file.
        """
        if os.path.exists(name_file) is True:
            os.remove(name_file)
        else:
            return False
