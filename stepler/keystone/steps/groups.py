"""
User steps.

@author: ssokolov@mirantis.com
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

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'GroupSteps'
]


class GroupSteps(BaseSteps):
    """Group steps."""

    @step
    def get_groups(self, domain='default', check=True):
        """Step to get groups."""
        groups = self._client.list(domain=domain)

        if check:
            assert groups
        return groups

    @step
    def find_group(self, name, domain='default', check=True):
        """Step to find group."""
        group = self._client.find(domain=domain, name=name)

        if check:
            assert group
        return group


