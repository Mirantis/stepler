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

import os

from hamcrest import assert_that, contains_string, is_in, is_not, equal_to  # noqa

from six import moves

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker


class CliGlanceSteps(base.BaseCliSteps):
    """CLI glance client steps."""

    @steps_checker.step
    def create_image(self, image_file=None, image_name=None, disk_format=None,
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
        image, exit_code, stdout, stderr = self.create_image(
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

    @steps_checker.step
    def download_image(self, image_file, file_path, file_option=True,
                       check=True):
        """Step to download image.

        Args:
            image_file(file): image file
            file_path(str): path of image file
            file_option(bool): flag for selecting of command
            check (bool): flag whether to check result or not

        Raises:
            AssertionError: if check failed
        """

        cmd = 'glance image-download'
        if file_option:
            cmd += ' --file {0} {1}'.format(file_path, image_file)
        else:
            cmd += ' {0} > {1}'.format(image_file, file_path)
        self.execute_command(cmd, check=check)
        if check:
            assert_that(os.path.exists(file_path), equal_to(True))
            assert_that(image_file.size,
                        equal_to(os.stat(file_path).st_size))
