"""
---------------
Glance steps v1
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

from glanceclient import exc as glance_exceptions
from hamcrest import assert_that, calling, raises  # noqa
from waiting import wait

from stepler.third_party import steps_checker

from .base import BaseGlanceSteps

__all__ = [
    'GlanceStepsV1',
]


class GlanceStepsV1(BaseGlanceSteps):
    """Glance steps for v1."""

    @steps_checker.step
    def create_images(self, image_names, image_path, disk_format='qcow2',
                      container_format='bare', check=True):
        """Step to create images.

        Args:
            image_names (list): names of created images
            image_path (str): path to image at local machine
            disk_format (str): format of image disk
            container_format (str): format of image container
            check (bool): flag whether to check step or not

        Returns:
            list: glance images
        """
        images = []

        for image_name in image_names:
            image = self._client.images.create(
                name=image_name,
                disk_format=disk_format,
                container_format=container_format)
            self._client.images.update(image=image,
                                       data=open(image_path, 'rb'))
            images.append(image)

        if check:
            for image in images:
                self.check_image_status(image, 'active', timeout=180)

        return images

    @steps_checker.step
    def check_delete_non_existing_image(self,
                                        image,
                                        check=True):
        """Step to delete non existed image

        Args:
            image (object): glance image
            check (bool): flag whether to check step or not

        Raises:
            HTTPNotFound: if image is not present.
        """
        assert_that(
            calling(self._client.images.delete).with_args(image.id),
            raises(glance_exceptions.HTTPNotFound))

    @steps_checker.step
    def check_image_presence(self, image, present=True, timeout=0):
        """Check step image presence status.

        Args:
            image (object): glance image to check presence status
            presented (bool): flag whether image should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        def predicate():
            deleted_image = self._client.images.get(image)
            if deleted_image.status == 'deleted':
                return not present
            else:
                return present

        wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def check_image_status(self, image, status, timeout=0):
        """Check step image status.

        Args:
            image (object): glance image to check status
            status (str): image status name to check
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        def predicate():
            new_image = self._client.images.get(image.id)
            setattr(image, 'status', new_image.status)
            return image.status.lower() == status.lower()

        wait(predicate, timeout_seconds=timeout)
