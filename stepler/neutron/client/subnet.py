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


class Subnet(base.Resource):
    pass


class SubnetManager(base.BaseNeutronManager):
    """Subnet (neutron) manager."""

    NAME = 'subnet'
    _resource_class = Subnet

    def create(self,
               name,
               network_id,
               cidr,
               ip_version=4,
               dns_nameservers=('8.8.8.8', '8.8.4.4'),
               project_id=None):
        """Create subnet action.

        Args:
            name (str): name of subnet
            network_id (str): id of the network to create subnet in it
            cidr (str): CIDR to create subnet with (for example: "10.0.0.0/24")
            ip_version (int): ip version (4 or 6)
            dns_nameservers (tuple of str): dns nameservers of subnet
            project_id (str|None): project id to create subnet in it. If None
                - subnet will be created in the current project

        Returns:
            dict: created subnet
        """
        query = {
            "network_id": network_id,
            "ip_version": ip_version,
            "cidr": cidr,
            "name": name
        }
        if dns_nameservers is not None:
            query['dns_nameservers'] = dns_nameservers
        if project_id is not None:
            query['tenant_id'] = project_id
        return super(SubnetManager, self).create(**query)

    def get_ports(self, subnet_id):
        """Return ports with interface to subnet."""
        subnet_ports = []
        for port in self.client.ports.list():
            if subnet_id in [ip['subnet_id'] for ip in port['fixed_ips']]:
                subnet_ports.append(port)
        return subnet_ports

    def get_fixed_ips(self, subnet_id):
        """Return subnet allocated fixed ip addresses."""
        for port in self.get_ports(subnet_id):
            for ip in port['fixed_ips']:
                if ip['subnet_id'] == subnet_id:
                    yield ip['ip_address']

    def delete(self, subnet_id):
        """Delete subnet action.

        Subnet can't be deleted until it has active ports, so we delete such
        ports before deleting subnet.
        """
        for port in self.get_ports(subnet_id):
            self.client.ports.delete(port['id'])
        return super(SubnetManager, self).delete(subnet_id)
