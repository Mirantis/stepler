"""
----------
Host steps
----------
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

from hamcrest import (assert_that, is_not, equal_to, empty,
                      greater_than_or_equal_to)  # noqa

from stepler import base
from stepler.third_party import steps_checker

__all__ = [
    'HostSteps'
]


class HostSteps(base.BaseSteps):
    """Host steps."""

    @steps_checker.step
    def get_hosts(self, check=True):
        """Step to get hosts.

        Args:
            check (bool): flag whether check step or not

        Returns:
            list: list of hosts objects

        Raises:
            AssertionError: if hosts list is empty
        """
        hosts = list(self._client.list())
        if check:
            assert_that(hosts, is_not(empty()))

        return hosts

    @steps_checker.step
    def get_host(self, name, check=True):
        """Step to get host by name.

        Args:
            name (str) - host name
            check (bool): flag whether check step or not

        Returns:
            list: list of hosts objects

        Raises:
            AssertionError: if host is not found
        """
        hosts = [host for host in self.get_hosts() if host.host_name == name]

        if check:
            assert_that(len(hosts), equal_to(1))

        return hosts[0]

    @steps_checker.step
    def get_usage_data(self, host, check=True):
        """Step to get cpu/memory/hdd data for host.

        # usage_data is the list of the following elements:
        # elem 0 - 'total' data, 1 - 'used now' data, 2 - 'used max' data
        # next elements - for VMs (one element per project)
        # Every element consists of cpu, memory_mb, disk_gb and other data
        # they are also duplicated in elem._info['resource']

        Args:
            host (object): host
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if hosts list are empty
        """
        usage_data = self._client.get(host.host_name)

        if check:
            assert_that(len(usage_data), greater_than_or_equal_to(3))

        return usage_data

    @steps_checker.step
    def check_usage_difference(self, usage_data_old, usage_data_new,
                               changed=True, project_id=None):
        """Step to check changes in host usages (cpu/memory/hdd)

        The following data are checked:
        - cp, memory_mb, disk_gb (for 'used now' and 'used max')
        - number of elements in usage_data (number of projects)
        - project id (only for checked=True)

        Args:
            usage_data_old (object): usage data in old state
            usage_data_new (object): usage data in new state
            changed (bool): indicator that some VMs are added/deleted
            project_id (str): project id of VMs created before (optional)

        Raises:
            AssertionError
        """

        # only 'used now' (elem 1) and 'used max' (elem 2) data are checked
        for ind in (1, 2):
            for attr in ['cpu', 'memory_mb', 'disk_gb']:
                value_old = usage_data_old[ind]._info['resource'][attr]
                value_new = usage_data_new[ind]._info['resource'][attr]
                if changed:
                    assert_that(value_new, is_not(equal_to(value_old)))
                else:
                    assert_that(value_new, equal_to(value_old))

        value_old = len(usage_data_old)
        value_new = len(usage_data_new)
        if changed:
            assert_that(value_new, is_not(equal_to(value_old)))
        else:
            assert_that(value_new, equal_to(value_old))

        if project_id:
            assert_that(project_id, equal_to(usage_data_new[-1].project))
