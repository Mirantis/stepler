"""
--------------
Router manager
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

from stepler.neutron.client import base

__all__ = ['RouterManager']


class RouterManager(base.BaseNeutronManager):
    """Router (neutron) manager."""

    def create(self, name, distributed):
        """Create router."""
        query = {'name': name,
                 'distributed': distributed}
        return super(RouterManager, self).create(**query)

    def add_gateway(self, router_id, network_id):
        """Add router gateway."""
        self._client._neutron_client.add_gateway_router(
            router_id, {'network_id': network_id})

    def remove_gateway(self, router_id):
        """Remove router gateway."""
        self._neutron_client.remove_gateway_router(router_id)

    def add_interface(self, router_id, subnet=None, port=None):
        """Add router interface."""
        body = self._get_interface_body(subnet, port)
        self._client._neutron_client.add_interface_router(router_id, body)

    def remove_interface(self, router_id, subnet=None, port=None):
        """Add router interface."""
        body = self._get_interface_body(subnet, port)
        self._client._neutron_client.remove_interface_router(router_id, body)

    @staticmethod
    def _get_interface_body(subnet=None, port=None):
        body = {}
        if subnet is not None:
            body['subnet_id'] = subnet['id']
        elif port is not None:
            body['port_id'] = port['id']
        else:
            raise ValueError("subnet_id or port_id must be indicated.")
        return body
