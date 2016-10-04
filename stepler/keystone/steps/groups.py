"""
-----------
Group steps
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

from hamcrest import assert_that, is_not, empty

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'GroupSteps'
]


class GroupSteps(BaseSteps):
    """Group steps."""

    @step
    def get_groups(self, domain='default', check=True):
        """Step to get groups.

        Args:
            domain (str or object): domain
            check (bool): flag whether to check step or not

        Returns:
            list of objects: list of groups
        """
        groups = list(self._client.list(domain=domain))

        if check:
            assert_that(groups, is_not(empty()))
        return groups

    @step
    def get_group(self, name, domain='default'):
        """Step to find group.

        Args:
            name (str) - group name
            domain (str or object): domain

        Raises:
            NotFound: if such group does not exist

        Returns:
            object: group
        """
        return self._client.find(name=name, domain=domain)
