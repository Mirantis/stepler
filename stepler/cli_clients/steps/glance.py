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

from hamcrest import (assert_that, contains_string, is_, is_in, is_not,
                      empty)  # noqa
from six import moves

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker
from stepler.third_party import utils


class CliGlanceSteps(base.BaseCliSteps):
    """CLI glance client steps."""

    @steps_checker.step
    def image_create(self, image_file=None, image_name=None, disk_format=None,
                     container_format=None,
                     api_version=config.CURRENT_GLANCE_VERSION,
                     check=True):
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
    def download_image(self,
                       image,
                       file_option=True,
                       timeout=config.IMAGE_DOWNLOAD_TIMEOUT,
                       check=True):
        """Step to download image.

        Args:
            image (object): glance image
            file_option (bool): flag to choice option ``download to file`` or
                to use stdout redirecting in order to safe image to file
            timeout (int, optional): seconds timeout to download glance image
            check (bool): flag whether to check result or not

        Returns:
            str: file path of downloaded image at remote machine

        Raises:
            AnsibleExecutionException: if image size is zero
        """
        file_path = '/tmp/' + next(utils.generate_ids())
        cmd = 'glance image-download'

        if file_option:
            cmd += ' --file {0} {1}'.format(file_path, image.id)
        else:
            cmd += ' {0} > {1}'.format(image.id, file_path)

        self.execute_command(cmd, timeout=timeout, check=check)

        if check:
            self.execute_command(  # check image size is non-zero
                cmd="[[ -s {} ]]".format(file_path),
                use_openrc=False)

        return file_path

    @steps_checker.step
    def show_image(self, image,
                   api_version=config.CURRENT_GLANCE_VERSION, check=True):
        """Step to show glance image.

        Args:
            image (obj): glance image
            api_version (int): the API version of Glance
            check (bool): flag whether to check result or not

        Returns:
            tuple: execution result (image_show, exit_code, stdout, stderr)

        Raises:
            AssertionError: if check failed
        """
        cmd = 'glance image-show {0}'.format(image.id)
        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version}, check=check)
        if check:
            image_table = output_parser.table(stdout)['values']
            image = {line[0]: line[1] for line in image_table}
        return image, exit_code, stdout, stderr

    @steps_checker.step
    def list_images(self, property_filter=None,
                    api_version=config.CURRENT_GLANCE_VERSION,
                    check=True):
        """Step to get glance images list.

        Args:
            property_filter (str): filter Glance images list
            api_version (int): the API version of Glance
            check (bool): flag whether to check result or not

        Returns:
            list: execution result: images_list

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        images = []
        cmd = 'glance image-list'
        if property_filter:
            if api_version == 2:
                cmd = '{} --property {}'.format(cmd, property_filter)
            else:
                cmd = '{} --property-filter {}'.format(cmd, property_filter)
        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version}, check=check)
        if check:
            images_table = output_parser.table(stdout)['values']
            if api_version == 1:
                # Take two first elements from information of each image
                # because it is id and name of image
                images_list = [img[0:2] for img in images_table]
                images = {id_img: name_img for id_img, name_img in images_list}
            else:
                images = {id_img: name_img for id_img, name_img
                          in images_table}
        return images

    @steps_checker.step
    def delete_image(self, image,
                     api_version=config.CURRENT_GLANCE_VERSION,
                     check=True):
        """Step to delete glance image.

        Args:
            image (obj): glance image
            api_version (int): API version of Glance
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'glance image-delete {0}'.format(image.id)
        self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version}, check=check)

    @steps_checker.step
    def check_image_list_contains(self, images,
                                  api_version=config.
                                  CURRENT_GLANCE_VERSION):
        """Step to check that image is in images list.

        Args:
            images (list): glance images
            api_version (int): the API version of Glance

        Raises:
            AssertionError: check failed if image is present in images list
        """
        all_images = self.list_images(api_version=api_version)
        assert_that(all_images, is_not(empty()))
        image_ids = all_images.keys()
        for image in images:
            assert_that(image['id'], is_in(image_ids))

    @steps_checker.step
    def check_image_list_doesnt_contain(self, images,
                                        api_version=config.
                                        CURRENT_GLANCE_VERSION):
        """Step to check that image doesn't exist in images list.

        Args:
            images (list): glance images
            api_version (int): the API version of Glance

        Raises:
            AssertionError: check failed if image doesn't present in
            images list
        """
        all_images = self.list_images(api_version=api_version)
        image_ids = all_images.keys()
        for image in images:
            assert_that(image['id'], is_not(is_in(image_ids)))

    @steps_checker.step
    def check_negative_image_create_without_properties(
            self, filename, api_version=config.CURRENT_GLANCE_VERSION):
        """Step to check image is not created from file without properties.

        Args:
            filename (str): filename (doesn't matter if it exists or not)
            api_version (int): glance api version (1 or 2)

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
    def check_negative_download_zero_size_image(
            self, image, progress=False,
            api_version=config.CURRENT_GLANCE_VERSION):
        """Step to check that zero-size image cannot be downloaded.

        Args:
            image (obj): glance image
            progress (bool): option of download command
            api_version (int): glance api version (1 or 2)

        Raises:
            AssertionError: if command exit code is 0 or stderr doesn't
                contain expected message.
        """
        cmd = "glance image-download {}".format(image.id)
        if progress:
            cmd += " --progress"
        if api_version == 1:
            error_message = ("Image {} is not active (HTTP 404)".
                             format(image.id))
        else:
            error_message = "Image {} has no data".format(image.id)

        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': int(api_version)},
            timeout=config.IMAGE_CREATION_TIMEOUT, check=False)

        assert_that(exit_code, is_not(0))
        assert_that(stderr, contains_string(error_message))

    @steps_checker.step
    def check_project_in_image_member_list(self, image, project,
                                           api_version=config.
                                           CURRENT_GLANCE_VERSION):
        """Step to check image member list.

        Args:
            image (obj): glance image
            project (obj): keystone project
            api_version (int): glance api version (1 or 2)

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
    def create_image_member(self, image, project,
                            api_version=config.CURRENT_GLANCE_VERSION,
                            check=True):
        """Step to create member for glance image.

        Args:
            image (obj): glance image
            project (obj): keystone project
            api_version (int): glance api version (1 or 2)
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'glance member-create {0} {1}'.format(image.id, project.id)
        self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version}, check=check)

    @steps_checker.step
    def delete_image_member(self, image, project,
                            api_version=config.CURRENT_GLANCE_VERSION,
                            check=True):
        """Step to delete member from glance image.

        Args:
            image (obj): glance image
            project (obj): keystone project
            api_version (int): glance api version (1 or 2)
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'glance member-delete {0} {1}'.format(image.id, project.id)
        self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version}, check=check)

    @steps_checker.step
    def check_negative_delete_non_existing_image(
            self, image,
            api_version=config.CURRENT_GLANCE_VERSION):
        """Step to check that we cannot delete removed image.

        Args:
            image(object): glance image
            api_version (int): glance api version (1 or 2)

        Raises:
            AssertionError: if command exit code is 0 or stderr doesn't
                contain expected message
        """
        cmd = "glance image-delete {}".format(image.id)

        error_message = ("No image with an ID of '{}' exists.".
                         format(image.id))

        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version},
            timeout=config.IMAGE_CREATION_TIMEOUT, check=False)

        assert_that(exit_code, is_not(0))
        assert_that(stderr, contains_string(error_message))

    @steps_checker.step
    def check_image_property(self, image,
                             property_key,
                             property_value,
                             api_version=config.CURRENT_GLANCE_VERSION):
        """Step to check that output of cli command `glance image-show <id>`
           contains updated property.

        Args:
            image (obj): glance image
            property_key (str): name of property for check
            property_value (str): value of property for check
            api_version (int): glance api version (1 or 2)

        Raises:
            AssertionError: if output of cli command `glance image-show <id>`
                doesn't contain updated property
        """
        image, exit_code, _, _ = self.show_image(
            image,
            api_version=api_version)

        if api_version == 1:
            property_key = "Property '{0}'".format(property_key)
        assert_that(image[property_key], is_(property_value))

    @steps_checker.step
    def check_images_filtered(self, images, property_filter,
                              api_version=config.CURRENT_GLANCE_VERSION):
        """Step to check that images list is filtered.

        Args:
            images (list): glance images
            property_filter (str): image field name to filter images
            api_version (int): glance api version (1 or 2)
        """
        for image in images:
            properties = property_filter + '=' + image[property_filter]
            filtered_images = self.list_images(property_filter=properties,
                                               api_version=api_version)
            assert_that(image['name'], is_in(filtered_images.values()))

    @steps_checker.step
    def remove_image_location(self, image, url, check=True):
        """Step to remove image location.

        Args:
            image (obj): glance image
            url (str): url for removing
            check (bool): flag whether to check result or not

        Returns:
            tuple: execution result (exit_code, stdout, stderr)

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'glance location-delete --url {0} {1}'.format(url, image.id)
        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': 2}, check=check)
        return exit_code, stdout, stderr

    @steps_checker.step
    def check_image_location_isnot_removed(self, image):
        """Step to check manipulating of image status via removing image location.

        Args:
            image (obj): glance image

        Raises:
            AssertionError: if last image location was removed
                with exit code=0 and stderr not correct
        """
        error_message = (
            "403 Forbidden: Access was denied to this resource.: "
            "Cannot remove last location in the image. (HTTP 403)")

        urls = [loc['url'] for loc in image.locations]

        # Remove all locations excluding last
        for url in urls[:-1]:
            self.remove_image_location(image, url)

        exit_code, _, stderr = self.remove_image_location(
            image, urls[-1],
            check=False)
        assert_that(exit_code, is_not(0))
        assert_that(stderr, is_(error_message))
