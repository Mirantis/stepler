"""
------------
Cinder quota steps
------------
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

from hamcrest import assert_that, greater_than  # noqa

from stepler import base
from stepler.third_party import steps_checker

__all__ = ['CinderQuotaSteps']


class CinderQuotaSteps(base.BaseSteps):
    """Cinder quota steps."""

    @steps_checker.step
    def get_volume_size_quota(self, session, check=True):
        """Step to retrieve quota for volume size.

        Args:
            check (bool): flag whether to check step or not
            session (obj): session object
        Returns:
            int: size in gigabytes

        Raises:
            AssertionError: if check was falsed
        """
        project_id = session.get_project_id()
        quota = self._client.defaults(project_id).gigabytes
        if check:
            assert_that(quota, greater_than(0))
        return quota
