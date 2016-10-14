"""
-----------
Auth steps
-----------
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
    'AuthSteps'
]


class AuthSteps(base.BaseSteps):
    """Keystone auth steps."""

    @steps_checker.step
    def get_auth_headers(self):
        """Step to get auth_headers."""
        auth_headers = self._client.get_auth_headers()

        return auth_headers
