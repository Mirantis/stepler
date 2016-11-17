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

from hamcrest import assert_that, equal_to, has_entries  # noqa

from stepler import base
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
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
            return expect_that(is_present, equal_to(must_present))

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
