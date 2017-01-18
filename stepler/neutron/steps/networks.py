"""
-------------
Network steps
-------------
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

from hamcrest import (assert_that, calling, empty, equal_to, has_entries,
                      has_length, is_, is_not, less_than, raises)  # noqa
from neutronclient.common import exceptions

from stepler import base
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = ["NetworkSteps"]


class NetworkSteps(base.BaseSteps):
    """Network steps."""

    @steps_checker.step
    def create(self, network_name, check=True, **kwargs):
        """Step to create network.

        Args:
            network_name (str): network name
            check (bool): flag whether to check step or not
            **kwargs: other arguments to pass to API

        Returns:
            dict: network
        """
        network = self._client.create(network_name, **kwargs)

        if check:
            self.check_presence(network)

        return network

    @steps_checker.step
    def delete(self, network, check=True):
        """Step to delete network.

        Args:
            network (dict): network
            check (bool): flag whether to check step or not
        """
        self._client.delete(network['id'])

        if check:
            self.check_presence(network, must_present=False)

    @steps_checker.step
    def check_presence(self, network, must_present=True, timeout=0):
        """Verify step to check network is present.

        Args:
            network (dict): network to check presence status
            must_present (bool): flag whether network must present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_network_presence():
            is_present = bool(self._client.find_all(id=network['id']))
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_network_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_network_by_name(self, name, **kwargs):
        """Step to get network by name.

        Args:
            name (str): network name
            **kwargs: other arguments to pass to API

        Returns:
            dict: network

        Raises:
            LookupError: if zero or more than one networks found
        """
        return self._client.find(name=name, **kwargs)

    @steps_checker.step
    def get_network(self, check=True, **kwargs):
        """Step to get network by params in '**kwargs'.

        Args:
            check (bool): flag whether to check step or not
            kwargs (dict): Params.
                           Like: {'router:external': True, 'status': 'ACTIVE'}

        Returns:
            dict: network
        """
        network = self._client.find(**kwargs)

        if check:
            assert_that(network, has_entries(kwargs))
        return network

    @steps_checker.step
    def get_networks(self, check=True, **kwargs):
        """Step to get networks by params in '**kwargs'.

        Args:
            check (bool, optional): flag whether to check step or not
            **kwargs: additional arguments to pass to API

        Returns:
            list: neutron networks

        Raises:
            AssertionError: if list of networks is empty
        """
        networks = list(self._client.find_all(**kwargs))
        if check:
            assert_that(networks, is_not(empty()))
        return networks

    @steps_checker.step
    def check_networks_are_accessible(self, must_be_accessible=True,
                                      timeout=0):
        """Step to check whether networks are accessible.

        Args:
            must_be_accessible (bool, optional): flag to wait for network
                accessibility or inaccessibility
            timeout (int): seconds to wait for result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def _check_networks_are_accessible():
            try:
                self.get_networks(check=False)
                is_run = True
            except Exception:
                is_run = False

            return waiter.expect_that(is_run, equal_to(must_be_accessible))

        waiter.wait(_check_networks_are_accessible,
                    timeout_seconds=timeout)

    @steps_checker.step
    def get_network_id_by_mac(self, mac):
        """Step to get network ID by server MAC.

        Args:
            mac (string): mac address
        Returns:
            string: network ID
        """
        network_id = self._client.client.ports.find_all(
            mac_address=mac)[0]['network_id']
        return network_id

    @steps_checker.step
    def get_dhcp_host_by_network(self, network_id):
        """Step to get DHCP host name by network ID."""
        result = self._client._rest_client.list_dhcp_agent_hosting_networks(
            network_id)
        nodes = [node for node in result['agents'] if node['alive'] is True]
        return nodes[0]['host']

    @steps_checker.step
    def get_networks_for_dhcp_agent(self, agent, check=True):
        """Step to get networks list for DHCP agent.

        Args:
            agent (dict): neutron agent dict to check status
            check (bool, optional): flag whether to check step or not

        Returns:
            list: list of networks for agent

        Raises:
            AssertionError: if check failed
        """
        networks = self._client.get_networks_for_dhcp_agent(agent['id'])
        if check:
            assert_that(networks, is_not(empty()))
        return networks

    @steps_checker.step
    def check_nets_count_for_agent(self, agent, expected_count):
        """Step to check networks count for DHCP agent.

        Args:
            agent (dict): neutron agent dict to check status
            expected_count (int): expected networks count for DHCP agents

        Raises:
            AssertionError: if check failed
        """
        networks = self.get_networks_for_dhcp_agent(agent, check=False)
        assert_that(networks, has_length(expected_count))

    @steps_checker.step
    def check_nets_count_difference_for_agents(self, dhcp_agents,
                                               max_difference_in_percent):
        """Step to check networks count for DHCP agent.

        This step verifies that the difference between max and min
        networks count for all DHCP agents is less than max allowed percent.
        Max networks count is considered to be 100%.

        Args:
            dhcp_agents (list): list of neutron agents dicts
            max_percentage_difference (int): max allowed percentage for
                difference between max and min nets counts for agents

        Raises:
            AssertionError: if check failed
        """

        def _count_percent_difference(min_val, max_val):
            diff = max_val - min_val
            result = (100 * diff) / float(max_val)
            return round(result)

        networks_count_on_agent = []

        for dhcp_agent in dhcp_agents:
            agent_networks = self.get_networks_for_dhcp_agent(dhcp_agent)
            networks_count_on_agent.append(len(agent_networks))

        min_count = min(networks_count_on_agent)
        max_count = max(networks_count_on_agent)
        actual_percentage_difference = _count_percent_difference(min_count,
                                                                 max_count)
        assert_that(actual_percentage_difference,
                    is_(less_than(max_difference_in_percent)))

    @steps_checker.step
    def check_negative_create_networks_more_than_limits(self, max_count):
        """"""
        exception_message = "Quota exceeded for resources"
        for _ in range(max_count):
            self.create(next(utils.generate_ids()))

        assert_that(
            calling(self.create).with_args(
                next(utils.generate_ids()), check=False),
            raises(exceptions.OverQuotaClient, exception_message))
