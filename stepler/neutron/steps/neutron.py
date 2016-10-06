"""
Neutron steps.

@author: schipiga@mirantis.com
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
        """Step to create network.

        Args:
            network_name (str): network name
            check (bool): flag whether to check step or not
        Returns:
            dict: network
        """
        body = {'network': {'name': network_name, 'admin_state_up': True}}
        network = self._client.create_network(body)['network']

        if check:
            self.check_network_presence(network)

        return network

    @step
    def delete_network(self, network, check=True):
        """Step to delete network.

        Args:
            network (dict): network
            check (bool): flag whether to check step or not
        """
        self._client.delete_network(network['id'])

        if check:
            self.check_network_presence(network, present=False)

    @step
    def check_network_presence(self, network, present=True, timeout=0):
        """Verify step to check network is present.

        Args:
            network (dict): network to check presence status
            presented (bool): flag whether network should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        def predicate():
            try:
                self._client.show_network(network['id'])
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def get_network(self, name):
        """Step to get network.

        Args:
            name (str): network volume
        Returns:
            dict: network
        Raises:
            LookupError: if zero or more than one networks fond
        """
        networks = self._client.list_networks(name=name)['networks']
        if len(networks) == 0:
            raise LookupError("Network {!r} is absent".format(name))
        elif len(networks) > 1:
            raise LookupError(
                "Fond {} networks with name {!r}".format(len(networks), name))
        return networks[0]

    @step
    def get_public_network(self):
        """Step to get publi network.

        Returns:
            dict: network
        """
        params = {'router:external': True,
                                             'status': 'ACTIVE'}
        return self._client.list_networks(**params)['networks'][0]

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

    @step
    def create_subnet(self, subnet_name, network, cidr, check=True):
        """Step to create subnet.

        Args:
            subnet_name (str): subnet name
            network (dict): network to create subnet on
            cidr (str): cidr for subnet (like 192.168.1.0/24"")
            check (bool): flag whether to check step or not
        Returns:
            dict: subnet
        """
        body = {'subnet': {"network_id": network['id'],
                           "ip_version": 4,
                           "cidr": cidr,
                           "name": subnet_name}}
        subnet = self._client.create_subnet(body)['subnet']

        if check:
            self.check_subnet_presence(subnet)

        return subnet

    @step
    def delete_subnet(self, subnet, check=True):
        """Step to delete subnet.

        Args:
            subnet (dict): subnet
            check (bool): flag whether to check step or not
        """
        self._client.delete_subnet(subnet['id'])

        if check:
            self.check_subnet_presence(subnet, present=False)

    @step
    def check_subnet_presence(self, subnet, present=True, timeout=0):
        """Verify step to check subnet is present.

        Args:
            subnet (dict): subnet to check presence status
            presented (bool): flag whether subnet should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        def predicate():
            try:
                self._client.show_subnet(subnet['id'])
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def create_router(self, router_name, distributed=False, check=True):
        """Step to create router.

        Args:
            router_name (str): router name
            distributed (bool): should router be distributed
            check (bool): flag whether to check step or not
        Returns:
            dict: router
        """
        body = {'router': {"distributed": distributed, "name": router_name}}
        router = self._client.create_router(body)['router']

        if check:
            self.check_router_presence(router)

        return router

    @step
    def delete_router(self, router, check=True):
        """Step to delete router.

        Args:
            router (dict): router
            check (bool): flag whether to check step or not
        """
        self._client.delete_router(router['id'])

        if check:
            self.check_router_presence(router, present=False)

    @step
    def check_router_presence(self, router, present=True, timeout=0):
        """Verify step to check router is present.

        Args:
            router (dict): router to check presence status
            presented (bool): flag whether router should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        def predicate():
            try:
                self._client.show_router(router['id'])
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def set_router_gateway(self, router, network, check=True):
        """Step to set router gateway.

        Args:
            router (dict): router
            network (dict): network
        """
        body = {
            'network_id': network['id']
        }
        self._client.add_gateway_router(router['id'], body)
        if check:
            self.check_router_gateway_presence(router)

    @step
    def clear_router_gateway(self, router, check=True):
        """Step to clear router gateway.

        Args:
            router (dict): router
        """
        self._client.remove_gateway_router(router['id'])
        if check:
            self.check_router_gateway_presence(router, present=False)

    @step
    def check_router_gateway_presence(self, router, present=True, timeout=0):
        """Verify step to check router gateway is present.

        Args:
            router (dict): router to check gateway presence status
            presented (bool): flag whether router should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        router_id = router['id']

        def predicate():
            router = self._client.show_router(router_id)['router']
            return present == (router['external_gateway_info'] is not None)

        wait(predicate, timeout_seconds=timeout)

    @step
    def add_router_subnet_interface(self, router, subnet, check=True):
        """Step to add router to subnet interface.

        Args:
            router (dict): router
            subnet (dict): subnet
        """
        body = {
            'subnet_id': subnet['id']
        }
        self._client.add_interface_router(router['id'], body)
        if check:
            self.check_router_interface_subnet_presence(router, subnet)

    @step
    def remove_router_subnet_interface(self, router, subnet, check=True):
        """Step to remove router to subnet interface.

        Args:
            router (dict): router
            subnet (dict): subnet
        """
        body = {
            'subnet_id': subnet['id']
        }
        self._client.remove_interface_router(router['id'], body)
        if check:
            self.check_router_interface_subnet_presence(router, subnet,
                                                        present=False)

    def _get_router_interface_ports(self, router):
        """Get router interface ports.

        Args:
            router (dict): router
        Returns:
            list: interface ports for router
        """
        return self._client.list_ports(device_owner='network:router_interface',
                                       device_id=router['id'])['ports']

    @step
    def check_router_interface_subnet_presence(self, router, subnet,
                                               present=True, timeout=0):
        """Verify step to check subnet is in router interfaces.

        Args:
            router (dict): router to check
            subnet (dict): subnet to find in router interfaces
            presented (bool): flag whether router should contains interface
                to subnet or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            ports = self._get_router_interface_ports(router)
            subnet_ids = [ip['subnet_id'] for p in ports
                          for ip in p['fixed_ips']]
            return present == (subnet['id'] in subnet_ids)

        wait(predicate, timeout_seconds=timeout)
