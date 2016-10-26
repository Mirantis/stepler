"""
----------------
Hypervisor steps
----------------
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

from hamcrest import assert_that, greater_than_or_equal_to  # noqa

from stepler import base
from stepler.third_party import steps_checker

__all__ = [
    'HypervisorSteps'
]


class HypervisorSteps(base.BaseSteps):
    """Hypervisor steps."""

    @steps_checker.step
    def get_hypervisors(self, min_number=1, check=True):
        """Step to get hypervisors.

        Args:
            min_number (int): min number of required hypervisors
                              (only with check=True)
            check (bool): flag whether check step or not

        Returns:
            list: list of hypervisors objects

        Raises:
            AssertionError: if hypervisors list are empty
        """

        hypervisors = list(self._client.list())
        if check:
            assert_that(len(hypervisors),
                        greater_than_or_equal_to(min_number))
        return hypervisors
