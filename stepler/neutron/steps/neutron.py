"""
-------------
Neutron steps
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

# TODO(schipiga): this module should be deleted because it's obsolete.
from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    "NeutronSteps"
]


class NeutronSteps(BaseSteps):
    """Neutron steps."""

    @step
    def create_network(self, network_name, check=True):
        """Step to create network."""
        network = self._client.create(network_name)['network']

        if check:
            self.check_network_presence(network)

        return network

    @step
    def delete_network(self, network, check=True):
        """Step to delete network."""
        self._client.delete(network['id'])

        if check:
            self.check_network_presence(network, present=False)

    @step
    def check_network_presence(self, network, present=True, timeout=0):
        """Verify step to check network is present."""
        def predicate():
            try:
                self._client.get(network['id'])
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def get_network(self, name):
        """Step to get network."""
        target_network = None
        networks = self._client.list_networks()['networks']
        for network in networks:
            if network['name'] == name:
                target_network = network
                break
        else:
            raise LookupError("Network {!r} is absent".format(name))

        return target_network

    @step
    def get_network_id_by_mac(self, mac):
        """Step to get network ID by server MAC."""
        network_id = self._client.list_ports(
            mac_address=mac)['ports'][0]['network_id']
        return network_id

    # TODO(schipiga): need refactor it after copy from mos-integration-tests.
    @step
    def get_dhcp_host_by_network(self, net_id, filter_attr='host',
                                 is_alive=True):
        """Step to get DHCP host name by network ID."""
        filter_fn = lambda x: x[filter_attr] if filter_attr else x
        result = self._client.list_dhcp_agent_hosting_networks(net_id)
        nodes = [filter_fn(node) for node in result['agents']
                 if node['alive'] == is_alive]
        return nodes[0]
