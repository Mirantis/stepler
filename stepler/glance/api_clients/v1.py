"""
--------------------
Glance API client v1
--------------------
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

from .base import BaseApiClient


class ApiClientV1(BaseApiClient):
    """Glance API client v1."""

    def images_update(self, image_id, status=None):
        """Update image via API call."""
        headers = self._auth_headers
        if status:
            headers['x-image-meta-status'] = status

        url = self._endpoint + '/v1/images/' + image_id
        self._put(url, headers)
