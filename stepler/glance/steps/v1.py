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

import requests

from stepler.glance.steps import base
from stepler.third_party import steps_checker

__all__ = [
    'GlanceStepsV1',
]


class GlanceStepsV1(base.BaseGlanceSteps):
    """Glance steps for v1."""

    @steps_checker.step
    def send_put_request_to_image_endpoint(self,
                                           image,
                                           auth_headers,
                                           headers=None,
                                           check=True):
        """Step to send put request to image endpoint.

        Args:
            image (object): image object
            auth_headers (dict): keystone session auth_headers
            headers (dict): additional headers to request
            check (bool): flag whether to check this step or not
        """
        headers = headers or {}
        headers.update(auth_headers)
        endpoint = self._client.http_client.get_endpoint()
        url = '{endpoint}/v1/images/{image_id}'.format(
            endpoint=endpoint, image_id=image.id)
        response = requests.put(url, headers=headers)
        if check:
            response.raise_for_status()
