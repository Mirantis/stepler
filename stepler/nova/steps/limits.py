"""
------------
Limits steps
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

from hamcrest import assert_that, empty, is_not  # noqa

from stepler.base import BaseSteps
from stepler.third_party import steps_checker

__all__ = [
    'LimitSteps'
]


class LimitSteps(BaseSteps):
    """Limits steps"""

    @steps_checker.step
    def get_absolute_limits(self, check=True, **kwgs):
        """Step to get absolute limits.

        Args:
            check (bool): flag whether to check step or not
            **kwgs (dict, optional): additional arguments to pass to API

        Returns:
            list: list of AbsoluteLimit objects
        """
        limits = list(self._client.get(**kwgs).absolute)

        if check:
            assert_that(limits, is_not(empty()))
        return limits
