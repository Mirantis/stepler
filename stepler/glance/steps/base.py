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
from hamcrest import assert_that, equal_to  # noqa
import warlock.model

from stepler import base
from stepler.third_party import steps_checker

__all__ = [
    'BaseGlanceSteps',
]


class BaseGlanceSteps(base.BaseSteps):
    """Glance base steps."""

    def _refresh_image(self, image):
        """Refresh local image data structure according to its type."""
        if isinstance(image, (glanceclient.v1.images.Image,
                              warlock.model.Model)):  # glanceclient

            fresh = self._client.images.get(image.id)
            data = getattr(fresh, '_info', fresh)
            getattr(image, '_info', image).update(data)

        else:  # stepler.base.Resource
            image.get()

    @steps_checker.step
    def update_images(self, images, status=None, check=True):
        """Step to update images."""
        kwgs = {}
        if status:
            kwgs['status'] = status

        for image in images:
            self._client.images.update(image.id, **kwgs)

        if check:
            for image in images:
                self._refresh_image(image)
                if status:
                    assert_that(image.status, equal_to(status))
