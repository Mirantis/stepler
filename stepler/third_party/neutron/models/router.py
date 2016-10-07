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

from stepler.third_party.neutron.models import base


class RouterManager(base.BaseNeutronManager):
    """Router (neutron) manager."""

    def create(self, name, distributed=False):
        """Create router."""
        query = {'name': name, 'distributed': distributed}
        return super(RouterManager, self).create(**query)

    def delete(self, router_id):
        """Delete router action.

        Router can't be deleted until it has interfaces, so we delete such
        ports before deleting router.
        """
        self.clear_gateway(router_id)
        for port in self.get_interfaces_ports(router_id):
            self.delete_interface_port(router_id, port_id=port['id'])

        super(RouterManager, self).delete(router_id)
