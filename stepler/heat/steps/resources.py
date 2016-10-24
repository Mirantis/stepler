"""
-------------------
Heat resource steps
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

from hamcrest import assert_that, equal_to, is_not, empty  # noqa

from stepler import base
from stepler.third_party import steps_checker

__all__ = ['ResourceSteps']


class ResourceSteps(base.BaseSteps):
    """Heat resource steps."""

    @steps_checker.step
    def get(self, stack, resource_name, check=True):
        """Step to create stack.

        Args:
            stack (obj): heat stack to check its status
            resource_name (str): desired resource name
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check was falsed after timeout
        """
        resource = self._client.get(stack.id, resource_name)
        if check:
            assert_that(resource, is_not(None))
        return resource
