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

from stepler import base

from stepler.third_party import steps_checker

__all__ = [
    'BaseGlanceSteps',
]


class BaseGlanceSteps(base.BaseSteps):
    """Glance base steps."""

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
        images = self.create_images([image_name],
                                    image_path,
                                    disk_format,
                                    container_format,
                                    check)
        return images[0]

    @steps_checker.step
    def delete_image(self, image, check=True):
        """Step to delete image.

        Args:
            image (object): glance image
            check (bool): flag whether to check step or not
        """
        self.delete_images([image], check)

    @steps_checker.step
    def delete_images(self, images, check=True):
        """Step to delete images.

        Args:
            image (object): glance image
            check (bool): flag whether to check step or not
        """
        for image in images:
            self._client.images.delete(image.id)

        if check:
            for image in images:
                self.check_image_presence(image, present=False, timeout=180)
