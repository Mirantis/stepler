"""
-------------------
Neutron quota steps
-------------------
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

from hamcrest import assert_that, is_not, empty, has_entries  # noqa H301

from stepler import base
from stepler.third_party import steps_checker

__all__ = ['QuotaSteps']


class QuotaSteps(base.BaseSteps):
    """Neutron quota steps."""

    @steps_checker.step
    def get(self, project, check=True):
        """Step to retrieve quota.

        Args:
            project (obj): project object
            check (bool|True): flag whether to check step or not

        Returns:
            dict: neutron quota values

        Raises:
            AssertionError: if check failed
        """
        quota = self._client.get(project.id)
        if check:
            assert_that(quota, is_not(empty()))
        return quota

    @steps_checker.step
    def update(self, project, values, check=True):
        """Step to update quota.

        Args:
            project (obj): project object
            values (dict): new quota values mapping
            check (bool|True): flag whether to check step or not

        Raises:
            AssertionError: if check was failed
        """
        self._client.update(project.id, **values)
        if check:
            new_quota = self.get(project)
            assert_that(new_quota, has_entries(**values))
