"""
--------------
Networks steps
--------------
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

import waiting

from stepler import base
from stepler.third_party import steps_checker

__all__ = ["NetworkSteps"]


class NetworkSteps(base.BaseSteps):
    @steps_checker.step
    def create(self, network_name, check=True):
        """Step to create network.

        Args:
            network_name (str): network name
            check (bool): flag whether to check step or not
        Returns:
            dict: network
        """
        network = self._client.create(network_name)

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
            self.check_presence(network, present=False)

    @steps_checker.step
    def check_presence(self, network, present=True, timeout=0):
        """Verify step to check network is present.

        Args:
            network (dict): network to check presence status
            presented (bool): flag whether network should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            exists = bool(self._client.find_all(id=network['id']))
            return exists == present

        waiting.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def get_network_by_name(self, name):
        """Step to get network by name.

        Args:
            name (str): network name
        Returns:
            dict: network
        Raises:
            LookupError: if zero or more than one networks fond
        """
        return self._client.find(name=name)

    @steps_checker.step
    def get_public_network(self):
        """Step to get public network.

        Returns:
            dict: network
        """
        params = {'router:external': True, 'status': 'ACTIVE'}
        return self._client.find(**params)

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
