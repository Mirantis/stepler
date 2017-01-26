"""
------------------
Nova service steps
------------------
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

from hamcrest import assert_that, is_not, equal_to, empty  # noqa

from stepler import base
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'NovaServiceSteps'
]


class NovaServiceSteps(base.BaseSteps):
    """Nova service steps."""

    @steps_checker.step
    def get_services(self, check=True):
        """Step to get nova services.

        Args:
            check (bool, optional): flag whether check step or not

        Returns:
            list: list of nova services

        Raises:
            AssertionError: if service list is empty
        """
        services = list(self._client.list())
        if check:
            assert_that(services, is_not(empty()))

        return services

    def _get_service_data(self, services):
        """Get service data used for checking (binary, host, status, state)

        Args:
            services (list): list of nova services

        Returns:
            list: list of service data, every element is the list of
                [binary, host, status, state]
        """
        service_data = []
        for service in services:
            data = []
            for key in ['binary', 'host', 'status', 'state']:
                data.append(getattr(service, key))
            service_data.append(data)
        return service_data

    @steps_checker.step
    def check_services_up(self, host_names=None, timeout=0):
        """Step to check that nova services are up.

        If host_names is specified service states atr checked only on
        these hosts.

        Args:
            host_names (list, optional): list of host names
            timeout (int, optional): seconds to wait result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_services_up():
            services = self.get_services()
            service_data = self._get_service_data(services)
            expected_service_data = []
            for data in service_data:
                binary, host_name = data[0:2]
                if host_names and host_name not in host_names:
                    expected_data = data
                else:
                    expected_data = [binary, host_name, 'enabled', 'up']
                expected_service_data.append(expected_data)
            return waiter.expect_that(service_data,
                                      equal_to(expected_service_data))

        waiter.wait(_check_services_up, timeout_seconds=timeout)

    @steps_checker.step
    def check_service_states(self, services, timeout=0):
        """Step to check states of nova services.

        This step checks that the current states of nova services are equal
        to expected ones.

        Args:
            services (list): list of nova services
            timeout (int): seconds to wait result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        expected_service_data = self._get_service_data(services)

        def _check_service_states():
            current_services = self.get_services()
            current_services_data = self._get_service_data(current_services)
            return waiter.expect_that(current_services_data,
                                      equal_to(expected_service_data))

        waiter.wait(_check_service_states, timeout_seconds=timeout)
