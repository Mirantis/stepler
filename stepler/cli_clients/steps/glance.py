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


from os import urandom
import tempfile

from stepler.cli_clients.steps import base
from stepler.third_party import steps_checker


class CliGlanceSteps(base.BaseCliSteps):
    """CLI glance client steps."""

    @steps_checker.step
    def glance_create_image_file(self, size=0, check=True):
        """Step to create file.

        Args:
            size (int): file size in MB
        """
        temp = tempfile.NamedTemporaryFile()
        temp.write(urandom(size * 1024))
        temp.close()
        return temp.name

    @steps_checker.step
    def glance_image_create_v1(self, image_name, image_file, check=True):
        """Step to create image.

        Args:
            image_name (str): name of created image
            image_file (str): image file to be uploaded
            check (bool): flag whether to check result or not

        Returns:
            str: result of command shell execution
        """
        cmd = ('glance image-create --name {} --container-format bare '
               '--disk-format qcow2 --file {}'.format(image_name, image_file))
        result = self.execute_command(cmd)
        if check:
            return result

    @steps_checker.step
    def glance_image_download_v1(self, image_name, image_file, check=True):
        """Step to download image.

        Args:
            image_name (str): name of image to download
            image_file (str): image file to be downloaded
            check (bool): flag whether to check result or not

        Returns:
            str: result of command shell execution
        """
        cmd = 'glance image-download -- file {} {}'.format(
            image_file, image_name)
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def glance_image_show_v1(self, image_name, check=True):
        """Step to show glance image.

        Args:
            image_name (str): name of image to show
            check (bool): flag whether to check result or not

        Returns:
            str: result of command shell execution
        """
        cmd = 'glance image-show {}'.format(image_name)
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def glance_image_list_v1(self, check=True):
        """Step to get glance list.

        Args:
            check (bool): flag whether to check result or not

        Returns:
            str: result of command shell execution
        """
        cmd = 'glance image-list'
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def glance_image_delete_v1(self, image_name, check=True):
        """Step to get glance list.

        Args:
            image_name (str): name of image to delete
            check (bool): flag whether to check result or not

        Returns:
            str: result of command shell execution
        """
        cmd = 'glance image-delete {}'.format(image_name)
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def glance_check_image_in_list(self, image_name, check=True):
        """Step to check if image exists in images list.

        Args:
            image_name (str): name of image to delete
            check (bool): flag whether to check result or not
        """
        images_list = self.glance_image_list_v1()
        assert image_name['id'] in [p['id'] for p in images_list]

    @steps_checker.step
    def glance_check_image_not_in_list(self, image_name, check=True):
        """Step to check if image doesn't exist in images list.

        Args:
            image_name (str): name of image to delete
            check (bool): flag whether to check result or not
        """
        images_list = self.glance_image_list_v1()
        assert image_name['id'] not in [p['id'] for p in images_list]
