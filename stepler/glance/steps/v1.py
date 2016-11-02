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

from stepler.third_party import steps_checker

from .base import BaseGlanceSteps

__all__ = [
    'GlanceStepsV1',
]


class GlanceStepsV1(BaseGlanceSteps):
    """Glance steps for v1."""

    @steps_checker.step
    def create_image(self, image_name, image_path, disk_format='qcow2',
                     container_format='bare', check=True):
        """Step to create image.

        Args:
            image_name (str): name of created image
            image_path (str): path to image at local machine
            disk_format (str): format of image disk
            container_format (str): format of image container
            check (bool): flag whether to check step or not

        Returns:
            object: glance image
        """
        image = self._client.images.create(name=image_name,
                                           disk_format=disk_format,
                                           container_format=container_format)
        return image

    @steps_checker.step
    def list_images(self, check=True):
        """Step to list images.

        Returns:
            list: list of glance images
        """
        images = list(self._client.images.list())

        return images

    @steps_checker.step
    def delete_image(self, image, check=True):
        """Step to delete image.

        Args:
            image (object): glance image
            check (bool): flag whether to check step or not
        """
        self._client.images.delete(image)
