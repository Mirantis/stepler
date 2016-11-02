# -*- coding: utf-8 -*-

"""
-----------------------
Glance CLI client steps
-----------------------
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
    def create_image_file(self, size=0, check=True):
        """Step to create file.

        Args:
            size (int): file size in MB
        """
        temp = tempfile.NamedTemporaryFile()
        temp.write(urandom(size * 1024))
        temp.close()
        return temp.name

    @steps_checker.step
    def image_create(self, image_name, image_file, check=True, version=1):
        """Step to create image.

        Args:
            image_name (str): name of created image
            image_file (str): image file to be uploaded
            check (bool): flag whether to check result or not
            version (int): set the API version of Glance

        Returns:
            str: result of command shell execution

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        flags = ("%(version)s %(name)s %(c-format)s %(d-format)s %(file)s"
                 % {'version': '--os-image-api-version %s' % version,
                    'name': '--name %s' % image_name,
                    'c-format': '--container-format bare ',
                    'd-format': '--disk-format qcow2 ',
                    'file': '--file %s' % image_file}
                 )
        cmd = 'glance image-create %s' % flags
        result = self.execute_command(cmd)
        if check:
            self.check_image_status(image_name)
            return result

    @steps_checker.step
    def image_download(self, image_name, image_file, check=True, version=1):
        """Step to download image.

        Args:
            image_name (str): name of image to download
            image_file (str): image file to be downloaded
            check (bool): flag whether to check result or not
            version (int): set the API version of Glance

        Returns:
            str: result of command shell execution
        """
        flags = ("%(version)s %(file)s %(name)s"
                 % {'version': '--os-image-api-version %s' % version,
                    'file': '--file %s' % image_file,
                    'name': '%s' % image_name})
        cmd = 'glance image-download %s' % flags
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def image_show(self, image_name, check=True, version=1):
        """Step to show glance image.

        Args:
            image_name (str): name of image to show
            check (bool): flag whether to check result or not
            version (int): set the API version of Glance

        Returns:
            str: result of command shell execution
        """
        flags = ("%(version)s %(name)s"
                 % {'version': '--os-image-api-version %s' % version,
                    'name': '%s' % image_name})
        cmd = 'glance image-show %s' % flags
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def image_list(self, check=True, version=1):
        """Step to get glance list.

        Args:
            check (bool): flag whether to check result or not
            version (int): set the API version of Glance

        Returns:
            str: result of command shell execution
        """
        cmd = 'glance --os-image-api-version %s image-list' % version
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def image_delete(self, image_name, check=True, version=1):
        """Step to get glance list.

        Args:
            image_name (str): name of image to delete
            check (bool): flag whether to check result or not
            version (int): set the API version of Glance

        Returns:
            str: result of command shell execution
        """
        flags = ("%(version)s %(name)s"
                 % {'version': '--os-image-api-version %s' % version,
                    'name': '%s' % image_name})
        cmd = 'glance image-delete %s' % flags
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def check_image_status(self, image_name):
        image_data = self.image_show(image_name)
        return image_data.status.lower() == 'queued'

    @steps_checker.step
    def check_image_in_list(self, image_name, check=True):
        """Step to check if image exists in images list.

        Args:
            image_name (str): name of image to delete
            check (bool): flag whether to check result or not
        """
        images_list = self.image_list()
        assert image_name['id'] in [image['id'] for image in images_list]

    @steps_checker.step
    def check_image_not_in_list(self, image_name, check=True):
        """Step to check if image doesn't exist in images list.

        Args:
            image_name (str): name of image to delete
            check (bool): flag whether to check result or not
        """
        images_list = self.image_list()
        assert image_name['id'] not in [image['id'] for image in images_list]

    @steps_checker.step
    def validate_unicode_support(self, check=True):
        if check:
            image_name = u"試験画像"
            image_file = self.create_image_file(size=1024)
            self.image_create(image_name, image_file)

            self.check_image_in_list(image_name)

            self.image_delete(image_name)
            self.check_image_not_in_list(image_name)
