"""
--------------------
Cinder API client v2
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

import json

from stepler.third_party import utils

from stepler import base

from .base import BaseApiClient


class ApiClientV2(BaseApiClient):
    """Cinder API client v2."""

    def volumes_create(self,
                       size,
                       name=None,
                       imageRef=None,
                       volume_type=None,
                       description=None,
                       snapshot_id=None):
        """Create volume."""
        name = name or next(utils.generate_ids('volume'))
        data = {
            'volume': {
                'size': size,
            }
        }
        if imageRef:
            data['volume']['imageRef'] = imageRef
        if volume_type:
            data['volume']['volume_type'] = volume_type
        if description:
            data['volume']['description'] = description
        if snapshot_id:
            data['volume']['snapshot_id'] = snapshot_id

        response = self._post('/volumes', data)
        return base.Resource(self, json.loads(response.json()))

    def volumes_get(self, volume_id):
        """Get volume."""
        response = self._get('/volumes/' + volume_id)
        return base.Resource(self, json.loads(response.json()))
