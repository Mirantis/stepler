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


class NetworkManager(base.BaseNeutronManager):
    """Neutwork (neutron) manager."""

    NAME = 'network'

    def create(self, name, project_id=None):
        """Create new neutron network.

        Args:
            name (str): name of the network
            project_id (str|None): project id to create network in it. If None
                - network will be created on current project

        Returns:
            dict: created network
        """
        kwargs = dict(name=name, admin_state_up=True)
        if project_id:
            kwargs['tenant_id'] = project_id
        return super(NetworkManager, self).create(**kwargs)

    def delete(self, network_id):
        """Delete network."""
        network = self.get(network_id)
        for subnet_id in network['subnets']:
            self.client.subnets.delete(subnet_id)
        super(NetworkManager, self).delete(network_id)
