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
    def get_resources(self, stack, name=None, check=True):
        """Step  to get list of resources.

        Args:
            stack (object): heat stack
            name (str): resource name
            check (bool): flag whether check step or not

        Returns:
            list: resource list for stack

        Raises:
            AssertionError: if check was falsed
        """
        resources = self._client.list(stack_id=stack.id)

        if name:
            resources = [resource for resource in resources
                         if resource.resource_name == name]

        if check:
            assert_that(resources, is_not(empty()))

        return resources

    @steps_checker.step
    def get_resource(self, stack, name):
        """Step  to get resource.

        Args:
            stack (object): heat stack
            name (str): resource name

        Returns:
            object: stack resource
        """
        return self.get_resources(stack, name)[0]
