"""
-----------------
Glance base steps
-----------------
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

import glanceclient.v1.images
from hamcrest import assert_that, equal_to, has_entries  # noqa
import warlock.model

from stepler import base
from stepler import config
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = [
    'BaseGlanceSteps',
]


class NotFound(Exception):
    """Not found exception."""


class BaseGlanceSteps(base.BaseSteps):
    """Glance base steps."""

    def _refresh_image(self, image):
        """Refresh local image data structure according to its type."""
        if isinstance(image, (glanceclient.v1.images.Image,
                              warlock.model.Model)):  # glanceclient

            images = [image_ for image_ in self._client.images.list()
                      if image_.id == image.id]
            if len(images) == 0:
                raise NotFound()
            fresh = images[0]
            data = getattr(fresh, '_info', fresh)
            getattr(image, '_info', image).update(data)

        else:  # stepler.base.Resource
            image.get()

    @steps_checker.step
    def update_images(self, images, status=None, check=True, **kwargs):
        """Step to update images.

        Args:
            images (list): glance images
            status (str): status of image for assertion
            check (bool): flag whether to check step or not
            **kwargs: like: {'name': 'TestVM'}

        Raises:
            AssertionError: if expected status not equal to actual status
        """
        if status:
            kwargs.update(status=status)

        for image in images:
            self._client.images.update(image.id, **kwargs)

        if check:
            for image in images:
                self._refresh_image(image)
                assert_that(image, has_entries(kwargs))
                if status:
                    assert_that(image.status, equal_to(status))

    @steps_checker.step
    def create_images(self,
                      image_path,
                      image_names=None,
                      disk_format='qcow2',
                      container_format='bare',
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
            upload (bool): flag whether to upload image after creation or not
                (upload=False is used in some negative tests)
            check (bool): flag whether to check step or not
            **kwargs: Optional. A dictionary containing the attributes
                        of the resource

        Returns:
            list: glance images

        Raises:
            AssertionError: if check failed
        """
        image_names = image_names or utils.generate_ids()

        images = []

        for image_name in image_names:

            image = self._client.images.create(
                name=image_name,
                disk_format=disk_format,
                container_format=container_format,
                **kwargs)

            if upload:
                self.upload_image(image, image_path, check=False)
            images.append(image)

        if check:
            for image in images:
                assert_that(image, has_entries(kwargs))
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
            except NotFound:
                is_present = False

            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_image_presence, timeout_seconds=timeout)
