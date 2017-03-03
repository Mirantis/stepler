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

from stepler.neutron.client import base


class Router(base.Resource):
    pass


class RouterManager(base.BaseNeutronManager):
    """Router (neutron) manager."""

    NAME = 'router'
    _resource_class = Router

    def create(self, name, distributed=None, project_id=None):
        """Create router.

        Args:
            name (str): name of router
            distributed (bool, optional): flag whatever router should be
                distributed or not. By default flag is not passed and type
                of router depends on neutron configuration.
            project_id (str|None): project id to create router on it. If None
                - router will create on current project

        Returns:
            dict: created router
        """
        query = {'name': name}
        if distributed is not None:
            query['distributed'] = distributed
        if project_id is not None:
            query['tenant_id'] = project_id
        return super(RouterManager, self).create(**query)

    def set_gateway(self, router_id, network_id):
        """Set router gateway."""
        body = {'network_id': network_id}
        self._rest_client.add_gateway_router(router_id, body)

    def clear_gateway(self, router_id):
        """Clear router gateway."""
        self._rest_client.remove_gateway_router(router_id)

    def get_interfaces_ports(self, router_id):
        """Get router interface ports."""
        router_ports = self.client.ports.find_all(device_id=router_id)
        dev_owner_values = ('network:router_interface',
                            'network:ha_router_replicated_interface',
                            'network:router_interface_distributed')
        return [
            port for port in router_ports
            if port['device_owner'] in dev_owner_values
        ]

    def get_router_interfaces_subnets_ids(self, router_id):
        """Get router interfaces subnets ids list."""
        ports = self.get_interfaces_ports(router_id)
        return [ip['subnet_id'] for p in ports for ip in p['fixed_ips']]

    def _add_interface(self, router_id, subnet_id=None, port_id=None):
        """Add router interface base action."""
        body = {}
        if subnet_id is not None:
            body['subnet_id'] = subnet_id
        elif port_id is not None:
            body['port_id'] = port_id
        else:
            raise ValueError("subnet_id or port_id must be indicated.")
        self._rest_client.add_interface_router(router_id, body)

    def add_subnet_interface(self, router_id, subnet_id):
        """Add router subnet interface."""
        self._add_interface(router_id=router_id, subnet_id=subnet_id)

    def add_port_interface(self, router_id, port_id):
        """Add router port interface.

        Args:
            router_id (str): router identifier
            port_id (str): port identifier
        """
        self._add_interface(router_id=router_id, port_id=port_id)

    def _remove_interface(self, router_id, subnet_id=None, port_id=None):
        """Remove router interface base action."""
        body = {}
        if subnet_id is not None:
            body['subnet_id'] = subnet_id
        elif port_id is not None:
            body['port_id'] = port_id
        else:
            raise ValueError("subnet_id or port_id must be indicated.")
        self._rest_client.remove_interface_router(router_id, body)

    def remove_subnet_interface(self, router_id, subnet_id):
        """Remove router subnet interface."""
        self._remove_interface(router_id=router_id, subnet_id=subnet_id)

    def remove_port_interface(self, router_id, port_id):
        """Remove router subnet interface."""
        self._remove_interface(router_id=router_id, port_id=port_id)

    def delete(self, router_id):
        """Delete router action.

        Router can't be deleted until it has interfaces, so we delete such
        ports before deleting router.
        """
        self.clear_gateway(router_id)
        for port in self.get_interfaces_ports(router_id):
            self.remove_port_interface(router_id, port_id=port['id'])

        super(RouterManager, self).delete(router_id)

    def get_routers_on_l3_agent(self, l3_agent_id):
        """Get a routers list of L3 agent."""
        routers = self._rest_client.list_routers_on_l3_agent(l3_agent_id)
        return routers[self.NAME + 's']
