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

from hamcrest import assert_that, is_not, empty  # noqa

from stepler import base
from stepler.third_party import steps_checker

__all__ = [
    'HypervisorSteps'
]


class HypervisorSteps(base.BaseSteps):
    """Hypervisor steps."""

    @steps_checker.step
    def get_hypervisors(self, check=True):
        """Step to get hypervisors.

        Args:
            check (bool): flag whether check step or not


        Returns:
            list: list of hyervisors objects

        Raises:
            AssertionError: if hypervisors list are empty
        """

        hypervisors = list(self._client.list())
        if check:
            assert_that(hypervisors, is_not(empty()))
        return hypervisors

    def get_hypervisor_capacity(self, hypervisor, flavor):
        """Step to get hypervisor capacity.

        This method calculates max available count of instances, which can be
        booted on hypervisor with choosed flavor.

        :returns: possible instances count

        Args:
            hypervisor (obj): nova hypervisor
            flavor (obj): nova flavor

        Returns:
            int: possible instances count
        """
        if hypervisor.vcpus < flavor.vcpus:
            return 0
        if flavor.disk > 0:
            return min(hypervisor.disk_available_least // flavor.disk,
                       hypervisor.free_ram_mb // flavor.ram)
        else:
            return hypervisor.free_ram_mb // flavor.ram
