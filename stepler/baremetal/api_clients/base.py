"""
----------------------
Ironic base API client
----------------------
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
from stepler import config


class IronicApiClient(base.BaseApiClient):
    """Ironic base API client."""

    @property
    def _endpoint(self):
        return self._session.get_endpoint(service_type='baremetal').rstrip('/')

    @property
    def _auth_headers(self):
        """Get auth headers.
        Returns:
            dict: authentication headers.
        """
        auth_headers = super(IronicApiClient, self)._auth_headers
        auth_headers.update({
            'User-Agent': 'python-ironicclient',
            'X-OpenStack-Ironic-API-Version':
                config.CURRENT_IRONIC_MICRO_VERSION
        })
        return auth_headers
