"""
----------
Port steps
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

from hamcrest import (assert_that, equal_to, empty,
                      has_entries, has_length, is_, is_not)  # noqa H301

from stepler import base
from stepler import config
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ["PortSteps"]


class PortSteps(base.BaseSteps):
    """Port steps."""

    @steps_checker.step
    def create(self, network, check=True):
        """Step to create port.

        Args:
            network (dict): network to create port on
            check (bool): flag whether to check step or not

        Returns:
            dict: port
        """
        port = self._client.create(network_id=network['id'])
        if check:
            self.check_presence(port)
        return port

    @steps_checker.step
    def delete(self, port, check=True):
        """Step to delete port.

        Args:
            port (dict): port to delete
            check (bool): flag whether to check step or not
        """
        if self._client.find_all(id=port['id']):
            self._client.delete(port['id'])
        if check:
            self.check_presence(port, must_present=False)

    @steps_checker.step
    def check_presence(self, port, must_present=True, timeout=0):
        """Verify step to check port is present.

        Args:
            port (dict): neutron port to check presence status
            must_present (bool): flag whether port must present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_port_presence():
            is_present = bool(self._client.find_all(id=port['id']))
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_port_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_port(self, check=True, **kwargs):
        """Step to get port by params in '**kwargs'.

        Args:
            check (bool): flag whether to check step or not
            **kwargs: params to filter port

        Returns:
            dict: port

        Raises:
            LookupError: if zero or more than one networks found
            AssertionError: if port attributes are wrong
        """
        port = self._client.find(**kwargs)

        if check:
            assert_that(port, has_entries(kwargs))
        return port

    @steps_checker.step
    def get_ports(self, check=True, **kwargs):
        """Step to retrieve all ports in current project.

        Args:
            check (bool): flag whether to check step or not
            **kwargs: params to list ports

        Returns:
            list: list of ports

        Raises:
            AssertionError: if list of ports is empty
        """
        ports = self._client.find_all(**kwargs)

        if check:
            assert_that(ports, is_not(empty()))

        return ports

    @steps_checker.step
    def check_equal_ports(self, ports_1, ports_2):
        """Step for comparing ports.

        Args:
            ports_1 (list): first list of ports for comparing
            ports_2 (list): second list of ports for comparing

        Raises:
            AssertionError: if lists are not equal
        """
        assert_that(sorted(ports_1), equal_to(sorted(ports_2)))

    @steps_checker.step
    def check_ports_ids_equal(self, ports_1, ports_2):
        """Step for comparing ports ids.

        Args:
            ports_1 (list): first list of ports for comparing ids
            ports_2 (list): second list of ports for comparing ids

        Raises:
            AssertionError: if ports ids of two lists are not equal
        """
        ports_ids_1 = [port['id'] for port in ports_1]
        ports_ids_2 = [port['id'] for port in ports_2]

        assert_that(sorted(ports_ids_1), equal_to(sorted(ports_ids_2)))

    @steps_checker.step
    def check_ports_binding_difference(self,
                                       ports_before,
                                       ports_after,
                                       expected_removed_count=None,
                                       expected_added_count=None):
        """Step for comparing ports bindings.

        Args:
            ports_before (list): first list of ports for comparing bindings
            ports_after (list): second list of ports for comparing bindings
            expected_removed_count (int): expected count of removed
                ports bindings
            expected_added_count (int): expected count of new
                ports bindings

        Raises:
            AssertionError: if actual removed or added count of bindings
                doesn't equal to their expected values
        """
        err_msg = ("At least one of `expected_removed_count` or "
                   "`expected_added_count` should be passed.")
        assert_that(any([expected_removed_count, expected_added_count]),
                    is_(True),
                    err_msg)

        ports_binding_before = {port[config.PORT_BINDING_HOST_ID]
                                for port in ports_before}
        ports_binding_after = {port[config.PORT_BINDING_HOST_ID]
                               for port in ports_after}

        if expected_removed_count is not None:
            actual_removed_count = ports_binding_before - ports_binding_after
            assert_that(actual_removed_count,
                        has_length(expected_removed_count))

        if expected_added_count is not None:
            actual_added_count = ports_binding_after - ports_binding_before
            assert_that(actual_added_count, has_length(expected_added_count))
