"""
---------------
Glance steps v2
---------------
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

from hamcrest import (assert_that, empty, equal_to,
                      has_items, is_not, is_in)  # noqa
from glanceclient import exc

from stepler import config
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

from .base import BaseGlanceSteps

__all__ = [
    'GlanceStepsV2',
]


class GlanceStepsV2(BaseGlanceSteps):
    """Glance steps for v2."""

    @steps_checker.step
    def create_images(self,
                      image_path,
                      image_names=None,
                      disk_format='qcow2',
                      container_format='bare',
                      visibility='private',
                      upload=True,
                      check=True,
                      **kwargs):
        """Step to create images.

        Args:
            image_path (str): path to image at local machine
            image_names (list): names of created images, if not specified
                one image name will be generated
            disk_format (str): format of image disk
            container_format (str): format of image container
            visibility (str): image visibility (private or public). Default is
                private.
            upload (bool): flag whether to upload image after creation or not
                (upload=False is used in some negative tests)
            check (bool): flag whether to check step or not
            **kwargs: Optional. A dictionary containing the attributes
                        of the resource

        Returns:
            list: glance images
        """
        image_names = image_names or utils.generate_ids()

        images = []

        for image_name in image_names:

            image = self._client.images.create(
                name=image_name,
                disk_format=disk_format,
                container_format=container_format,
                visibility=visibility,
                **kwargs)

            if upload:
                self._client.images.upload(image.id, open(image_path, 'rb'))
            images.append(image)

        if check:
            for image in images:
                if upload:
                    self.check_image_status(
                        image,
                        config.STATUS_ACTIVE,
                        timeout=config.IMAGE_AVAILABLE_TIMEOUT)
                else:
                    self.check_image_status(
                        image,
                        config.STATUS_QUEUED,
                        timeout=config.IMAGE_QUEUED_TIMEOUT)

        return images

    @steps_checker.step
    def delete_images(self, images, check=True):
        """Step to delete images.

        Args:
            images (object): glance images
            check (bool): flag whether to check step or not
        """
        for image in images:
            self._client.images.delete(image.id)

        if check:
            for image in images:
                self.check_image_presence(
                    image,
                    must_present=False,
                    timeout=config.IMAGE_AVAILABLE_TIMEOUT)

    @steps_checker.step
    def bind_project(self, image, project, check=True):
        """Step to bind image to project.

        Args:
            image (object): image to bind to project
            project (object): project to bind to image
            check (bool): flag whether to check binding or not
        """
        self._client.image_members.create(image.id, project.id)
        if check:
            self.check_image_bind_status(image, project)

    @steps_checker.step
    def unbind_project(self, image, project, check=True):
        """Step to unbind image to project.

        Args:
            image (object): image to unbind from project
            project (object): project to unbind from image
            check (bool): flag whether to check unbinding or not
        """
        self._client.image_members.delete(image.id, project.id)
        if check:
            self.check_image_bind_status(image, project, must_bound=False)

    @steps_checker.step
    def get_images(self, name_prefix=None, check=True, **kwargs):
        """Step to retrieve images from glance.

        Args:
            name_prefix (str): name prefix to filter images
            check (bool): flag whether to check step or not
            **kwargs: like: {'name': 'TestVM', 'status': 'active'}

        Returns:
            list: images list

        Raises:
            AssertionError: if check triggered an error
        """
        images = list(self._client.images.list())

        if name_prefix:
            images = [image for image in images
                      if (image.name or '').startswith(name_prefix)]

        if kwargs:
            matched_images = []
            for image in images:
                for key, value in kwargs.items():
                    if not (key in image and image[key] == value):
                        break
                else:
                    matched_images.append(image)
            images = matched_images

        if check:
            assert_that(images, is_not(empty()))

        return images

    @steps_checker.step
    def get_image(self, check=True, **kwargs):
        """Find one image by provided **kwargs.

        Args:
            check (bool): flag whether to check step or not
            **kwargs: like: {'name': 'TestVM', 'status': 'active'}

        Returns:
            object: glance image

        Raises:
            ValueError: if '**kwargs' were not provided
        """
        if not kwargs:
            raise ValueError("Need to provide search criteria.")

        images = self.get_images(check=check, **kwargs)
        return images[0]

    @steps_checker.step
    def check_image_presence(self, image, must_present=True, timeout=0):
        """Check step image presence status.

        Args:
            image (object): glance image to check presence status
            must_present (bool): flag whether image should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_image_presence():
            try:
                self._refresh_image(image)
                is_present = True
            except exc.NotFound:
                is_present = False

            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_image_presence, timeout_seconds=timeout)

    @steps_checker.step
    def check_image_status(self, image, status, timeout=0):
        """Check step image status.

        Args:
            image (object): glance image to check status
            status (str): image status name to check
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_image_status():
            self._refresh_image(image)
            return waiter.expect_that(image.status.lower(),
                                      equal_to(status.lower()))

        waiter.wait(_check_image_status, timeout_seconds=timeout)

    @steps_checker.step
    def check_image_bind_status(self,
                                image,
                                project,
                                must_bound=True,
                                timeout=0):
        """Check step image binding status.

        Args:
            image (object): image bound/unbound with project
            project (object): project bound/unbound with image
            must_bound (bool): flag whether project and image should be bound
                or unbound
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_image_bind_status():
            members = self._client.image_members.list(image.id)
            member_ids = [member['member_id'] for member in members]
            if must_bound:
                assert_that(project.id, is_in(member_ids))
                is_bound = True
            else:
                is_bound = False

            return waiter.expect_that(is_bound, equal_to(must_bound))

        waiter.wait(_check_image_bind_status, timeout_seconds=timeout)

    @steps_checker.step
    def check_image_container_and_disk_format(self,
                                              image_name,
                                              image_container,
                                              disk_format):
        """Check image container format and disk format.

        Args:
            image_name (object): image bound/unbound with project
            image_container (str): type of image container
            disk_format (str): type of disk format

        Raises:
            AssertionError: if check failed
        """
        image = self.get_image(name=image_name)
        assert_that(image['container_format'], equal_to(image_container))
        assert_that(image['disk_format'], equal_to(disk_format))

    @steps_checker.step
    def check_that_image_id_is_changed(self, image_name, image_id):
        """Step to check that after updating heat stack image_id was changed.

        Args:
            image_name (str): image name that was replaced
            image_id (str): before updating

        Raises:
            AssertionError: if check failed
        """
        image_id_changed = self.get_image(name=image_name)['id']
        assert_that(image_id_changed, is_not(image_id))

    @steps_checker.step
    def check_image_hash(self, image_path_1, image_path_2):
        """Step to check hash sum of uploaded image and downloaded image.

        Args:
            image_path_1 (str): path to first image
            image_path_2 (str): path to second image

        Raises:
            AssertionError: if hash sum has been mismatched
        """
        image_md5_1 = utils.get_md5sum(image_path_1)
        image_md5_2 = utils.get_md5sum(image_path_2)
        assert_that(image_md5_1, equal_to(image_md5_2))

    @steps_checker.step
    def check_image_data_corresponds_to_source(self, image, file_path):
        """Step to check that image data correspond to image source.

        Args:
            image (obj): image object
            file_path (str): path to file image upload from

        Raises:
            AssertionError: if image checksum not equal to source file checksum
        """
        assert_that(image.checksum, equal_to(utils.get_md5sum(file_path)))

    @steps_checker.step
    def check_glance_service_available(self, should_be=True):
        """Step to check glance service availability.

        Args:
            should_be (bool): flag whether glance should available or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_available():
            try:
                self.get_images(check=False)
                is_available = True
            except exc.HTTPServiceUnavailable:
                is_available = False
            return waiter.expect_that(is_available, equal_to(should_be))

        waiter.wait(_check_available,
                    timeout_seconds=config.GLANCE_AVAILABILITY_TIMEOUT)

    @steps_checker.step
    def add_locations(self, image, urls, check=True):
        """Step to add location to image.

        Args:
            image (obj): glance image
            urls (list): urls for adding to image location
            check (bool): flag whether to check step or not
        """
        for url in urls:
            self._client.images.add_location(
                image.id,
                url=url,
                metadata={}
            )
        if check:
            self._refresh_image(image)
            locations = [loc['url'] for loc in image.locations]
            assert_that(locations, has_items(*urls))
