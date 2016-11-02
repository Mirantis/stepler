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

from hamcrest import assert_that, contains_string, equal_to  # noqa
from os import urandom
from six import moves
import tempfile

from stepler.cli_clients.steps import base
from stepler.third_party import output_parser
from stepler.third_party import steps_checker


class CliGlanceSteps(base.BaseCliSteps):
    """CLI glance client steps."""

    @steps_checker.step
    def image_file_create(self, size=0, check=True):
        """Step to create file.

        Args:
            size (int): file size in MB
            check (bool): flag whether to check result or not
        """
        temp = tempfile.NamedTemporaryFile()
        temp.write(urandom(size * 1024))
        temp.close()
        return temp.name

    @steps_checker.step
    def image_create(self, image_file, disk_format, container_format,
                     image_name=None, api_version=2, check=True):
        """Step to create image.

        Args:
            image_file (str): image file to be uploaded
            image_name (str): name of created image
            disk_format (str): disk format of image
            container_format (str): container format of image
            api_version (int): API version of Glance
            check (bool): flag whether to check result or not

        Returns:
            tuple: execution result (image dict, exit_code, stdout, stderr)

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        image = None
        cmd = 'glance image-create'
        if image_file:
            cmd += ' --file ' + moves.shlex_quote(image_file)
        if image_name:
            cmd += ' --name ' + moves.shlex_quote(image_name)
        if disk_format:
            cmd += ' --disk-format ' + disk_format
        if container_format:
            cmd += ' --container-format ' + container_format

        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version},
            check=check)

        if check:
            image_table = output_parser.table(stdout)
            image = {key: value for key, value in image_table['values']}

        return image, exit_code, stdout, stderr

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
        flags = ('--os-image-api-version %s --file %s %s'.format(version,
                                                                 image_file,
                                                                 image_name))
        cmd = 'glance image-download %s'.format(flags)
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

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        flags = ('--os-image-api-version %s %s'.format(version, image_name))
        cmd = 'glance image-show %s'.format(flags)
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
        cmd = 'glance --os-image-api-version %s image-list'.format(version)
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def image_delete(self, image_name, check=True, version=1):
        """Step to delete glance image.

        Args:
            image_name (str): name of image to delete
            check (bool): flag whether to check result or not
            version (int): set the API version of Glance

        Returns:
            str: result of command shell execution
        """
        flags = ('--os-image-api-version %s %s'.format(version, image_name))
        cmd = 'glance image-delete %s'.format(flags)
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def check_image_status(self, image_name, check=True):
        image_data = self.image_show(image_name, check=check)
        return image_data.status.lower() == 'queued'

    @steps_checker.step
    def check_image_in_list(self, image_name, check=True):
        """Step to check if image exists in images list.

        Args:
            image_name (str): name of image to check
            check (bool): flag whether to check result or not
        """
        images_list = self.image_list()
        assert image_name['id'] in [image['id'] for image in images_list]

    @steps_checker.step
    def check_image_not_in_list(self, image_name, check=True):
        """Step to check if image doesn't exist in images list.

        Args:
            image_name (str): name of image to check
            check (bool): flag whether to check result or not
        """
        images_list = self.image_list()
        assert image_name['id'] not in [image['id'] for image in images_list]

    @steps_checker.step
    def check_unicode_support(self):
        image_name = u"試験画像"
        image_file = self.create_image_file(size=1024)
        self.image_create(image_name=image_name,
                          image_file=image_file,
                          disk_format='qcow2',
                          container_format='bare',
                          api_version=1,
                          check=False
                          )
        self.check_image_status(image_name, check=False)

        self.check_image_in_list(image_name, check=False)

        self.image_delete(image_name, check=False)
        self.check_image_not_in_list(image_name, check=False)

    @steps_checker.step
    def check_negative_image_create_without_properties(self, filename,
                                                       api_version=2):
        """Step to check image is not created from file without properties.

        Args:
            filename (str): filename (doesn't matter if it exists or not)
            api_version (int): glance api version (1 or 2). Default is 2

        Raises:
            AssertionError: if command exit code is not 1 or stderr doesn't
                contain expected message
        """
        error_message = ("Must provide --container-format, "
                         "--disk-format when using --file.")
        image, exit_code, stdout, stderr = self.create_image(
            image_file=filename,
            disk_format=None,
            container_format=None,
            api_version=api_version,
            check=False)
        assert_that(exit_code, equal_to(1))
        assert_that(stderr, contains_string(error_message))
