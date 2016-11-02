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

from hamcrest import (assert_that, contains_string,
                      equal_to, is_not, is_in)  # noqa H301
from six import moves

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker


class CliGlanceSteps(base.BaseCliSteps):
    """CLI glance client steps."""

    @steps_checker.step
    def image_create(self, image_file=None, image_name=None, disk_format=None,
                     container_format=None, api_version=2, check=True):
        """Step to create image.

        Args:
            image_file (str|None): image file to be uploaded; it should be
                located on the same node where CLI is running
            image_name (str|None): name of created image
            disk_format (str|None): disk format of image
            container_format (str|None): container format of image
            api_version (int): API version of Glance (1 or 2)
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
        if 'disk-format' not in cmd and 'container-format' not in cmd:
            cmd += ' <&-'
            # otherwise stderr: <stdin: is not a tty\nerror: Must provide
            # --container-format, --disk-format when using stdin>
            # This problem is only for remote execution (Ansible)

        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version},
            check=check)

        if check:
            image_table = output_parser.table(stdout)
            image = {key: value for key, value in image_table['values']}

        return image, exit_code, stdout, stderr

    @steps_checker.step
    def image_download(self, image_name, image_file, check=True,
                       api_version=2):
        """Step to download image.

        Args:
            image_name (str): name of image to download
            image_file (str): image file to be downloaded
            check (bool): flag whether to check result or not
            api_version (int): set the API version of Glance

        Returns:
            tuple: execution result (exit_code, stdout, stderr)
        """
        flags = ('--os-image-api-version {} --file {} {}'.format(api_version,
                                                                 image_file,
                                                                 image_name))
        cmd = 'glance image-download {}'.format(flags)
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def image_show(self, image_name, check=True, api_version=2):
        """Step to show glance image.

        Args:
            image_name (str): name of image to show
            check (bool): flag whether to check result or not
            api_version (int): set the API version of Glance

        Returns:
            tuple: execution result (image_dict, exit_code, stdout, stderr)

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        flags = ('--os-image-api-version {} {}'.format(api_version,
                                                       image_name))
        cmd = 'glance image-show {}'.format(flags)
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def image_list(self, check=True, api_version=2):
        """Step to get glance list.

        Args:
            check (bool): flag whether to check result or not
            api_version (int): set the API version of Glance

        Returns:
            tuple: execution result (image_dict, exit_code, stdout, stderr)
        """
        cmd = 'glance --os-image-api-version {} image-list'.format(api_version)
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def image_delete(self, image_name, check=True, api_version=2):
        """Step to delete glance image.

        Args:
            image_name (str): name of image to delete
            check (bool): flag whether to check result or not
            api_version (int): set the API version of Glance

        Returns:
            tuple: execution result (exit_code, stdout, stderr)
        """
        flags = ('--os-image-api-version {} {}'.format(api_version,
                                                       image_name))
        cmd = 'glance image-delete {}'.format(flags)
        result = self.execute_command(cmd, check=check)
        return result

    @steps_checker.step
    def get_image_status(self, image_name, api_version=2):
        """Step to check that image status is queued

        Args:
            image_name (str): name of image to check
            api_version (int): set the API version of Glance
        """
        image_show = self.image_show(image_name, api_version=api_version)
        return image_show[0].status.lower() == 'queued'

    @steps_checker.step
    def check_image_in_list(self, image_name, api_version=2):
        """Step to check if image exists in images list.

        Args:
            image_name (str): name of image to check
            api_version (int): set the API version of Glance

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        image_show = self.image_show(image_name=image_name,
                                     api_version=api_version)
        images_list = self.image_list(api_version=api_version)
        assert_that(image_show['id'],
                    is_in([image['id'] for image in images_list]))

    @steps_checker.step
    def check_image_not_in_list(self, image_name, api_version=2):
        """Step to check if image doesn't exist in images list.

        Args:
            image_name (str): name of image to check
            api_version (int): set the API version of Glance

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        image_show = self.image_show(image_name=image_name,
                                     api_version=api_version)
        images_list = self.image_list(api_version=api_version)
        assert_that(image_show['id'],
                    is_not(is_in([image['id'] for image in images_list])))

    @steps_checker.step
    def check_unicode_support(self, image_name, api_version=1):
        """Step to check unicode support in glance cli.

        Args:
            image_name (str): name of image to check
            api_version (int): glance api version (1 or 2). Default is 2
        """
        self.get_image_status(image_name, check=False, api_version=api_version)

        self.check_image_in_list(image_name=image_name,
                                 api_version=api_version)
        self.image_delete(image_name, check=False, api_version=api_version)
        self.check_image_not_in_list(image_name, api_version=api_version)

    @steps_checker.step
    def check_negative_image_create_without_properties(self, filename,
                                                       api_version=2):
        """Step to check image is not created from file without properties.

        Args:
            filename (str): filename (doesn't matter if it exists or not)
            api_version (int): glance api version (1 or 2). Default is 2

        Raises:
            AssertionError: if command exit code is 0 or stderr doesn't
                contain expected message
        """
        error_message = ("Must provide --container-format, "
                         "--disk-format when using --file.")
        image, exit_code, stdout, stderr = self.image_create(
            image_file=filename,
            disk_format=None,
            container_format=None,
            api_version=api_version,
            check=False)
        assert_that(exit_code, is_not(0))
        assert_that(stderr, contains_string(error_message))

    @steps_checker.step
    def check_negative_download_zero_size_image(self, image_id,
                                                progress=False,
                                                api_version=2):
        """Step to check that zero-size image cannot be downloaded.

        Args:
            image_id (str): image ID
            progress (bool): option of download command
            api_version (int): glance api version (1 or 2). Default is 2

        Raises:
            AssertionError: if command exit code is 0 or stderr doesn't
                contain expected message.
        """
        cmd = "glance image-download {}".format(image_id)
        if progress:
            cmd += " --progress"
        if api_version == 1:
            error_message = ("Image {} is not active (HTTP 404)".
                             format(image_id))
        else:
            error_message = "Image {} has no data".format(image_id)

        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': int(api_version)},
            timeout=config.IMAGE_CREATION_TIMEOUT, check=False)

        assert_that(exit_code, is_not(0))
        assert_that(stderr, contains_string(error_message))

    @steps_checker.step
    def check_project_in_image_member_list(self, image, project,
                                           api_version=2):
        """Step to check image member list.

        Args:
            image (obj): glance image
            project (obj): keystone project
            api_version (int): glance api version (1 or 2). Default is 2

        Raises:
            AnsibleExecutionException: if command execution failed
            AssertionError: if project is not in image member list
        """
        cmd = 'glance member-list --image-id {0}'.format(image.id)

        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version})
        member_table = output_parser.listing(stdout)
        project_ids = [member['Member ID'] for member in member_table]

        assert_that(project.id, is_in(project_ids))

    @steps_checker.step
    def create_image_member(self, image, project, api_version=2, check=True):
        """Step to create member for glance image.

        Args:
            image (obj): glance image
            project (obj): keystone project
            api_version (int): glance api version (1 or 2). Default is 2
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'glance member-create {0} {1}'.format(image.id, project.id)
        self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version}, check=check)

    @steps_checker.step
    def delete_image_member(self, image, project, api_version=2, check=True):
        """Step to delete member from glance image.

        Args:
            image (obj): glance image
            project (obj): keystone project
            api_version (int): glance api version (1 or 2). Default is 2
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'glance member-delete {0} {1}'.format(image.id, project.id)
        self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version}, check=check)
