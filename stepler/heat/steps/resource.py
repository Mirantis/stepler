"""
----------------
Heat stack steps
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

from hamcrest import assert_that, is_not, empty  # noqa

from stepler import base

from stepler.third_party import steps_checker

__all__ = ['ResourceSteps']


class ResourceSteps(base.BaseSteps):
    """Heat resource list"""

    @steps_checker.step
    def get_resource_list(self, stack, check=True):
        """Step  to get list of resources

        Args:
            stack (object): heat stack
            check (bool): flag whether check step or not

        Returns:
            list: resource list for stack

        Raises:
            AssertionError: if check was falsed
        """
        resource_list = self._client.list(stack_id=stack.id)

        if check:
            assert_that(resource_list, is_not(empty()))

        return resource_list

    @steps_checker.step
    def check_physical_resource_id_changed(self,
                                           physical_resource_id,
                                           stack,
                                           check=True):
        """Step to check that after updating stack
        physical_resource_id was chanched.

        Args:
            physical_resource_id (str): befor updating
            stack (object): heat stack
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if check was falsed
        """
        physical_resource_id_changed = self.get_resource_list(
            stack)[0].physical_resource_id

        if check:
            assert_that(physical_resource_id_changed,
                        is_not(physical_resource_id))
