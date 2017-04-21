"""
------------
Port manager
------------
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


class Port(base.Resource):
    pass


class PortManager(base.BaseNeutronManager):
    """Port (neutron) manager."""

    NAME = 'port'
    _resource_class = Port

    def delete(self, port_id):
        """Delete a port.

        Args:
            port_id (str): port identifier
        """
        port = self.get(port_id)
        if port['device_owner'] == 'network:router_interface':
            self.client.routers.remove_port_interface(
                port['device_id'], port_id)
        # If port wasn't deleted - delete it
        if self.find_all(id=port_id):
            super(PortManager, self).delete(port_id)

    @base.filter_by_project
    def find_all(self, **kwargs):
        return super(PortManager, self).find_all(**kwargs)
