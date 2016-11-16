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


class RouterManager(base.BaseNeutronManager):
    """Router (neutron) manager."""

    NAME = 'router'

    def create(self, name, distributed=False, project_id=None):
        """Create router.

        Args:
            name (str): name of router
            distributed (bool): flag whatever router should be distributed or
                not; flag will be passed only if it is True,
                it is False by default in neutronclient
            project_id (str|None): project id to create router on it. If None
                - router will create on current project

        Returns:
            dict: created router
        """
        query = {'name': name}
        if distributed is True:
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
        return self.client.ports.find_all(
            device_owner='network:router_interface',
            device_id=router_id)

    def get_interfaces_subnets_ids(self, router_id):
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
