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

from stepler import config
from stepler.glance.steps import base
from stepler.third_party import steps_checker


__all__ = [
    'GlanceStepsV1',
]


class GlanceStepsV1(base.BaseGlanceSteps):
    """Glance steps for v1."""

    @steps_checker.step
    def upload_image(self, image, image_path, check=True):
        """Step to upload image.

        Args:
            image (obj): glance image
            image_path (str): path image file
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError: if check failed
        """
        with open(image_path, 'rb') as f:
            self._client.images.update(image.id, data=f)

        if check:
            self.check_image_status(
                image,
                config.STATUS_ACTIVE,
                timeout=config.IMAGE_AVAILABLE_TIMEOUT)
