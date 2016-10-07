"""
--------------
Subnet manager
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

__all__ = ['SubnetManager']


class SubnetManager(base.BaseNeutronManager):
    """Subnet (neutron) manager."""

    def create(self,
               name,
               network_id,
               cidr,
               ip_version=4,
               dns_nameservers=('8.8.8.8', '8.8.4.4')):
        """Create subnet action."""
        query = {
            "network_id": network_id,
            "ip_version": ip_version,
            "cidr": cidr,
            "name": name
        }
        if dns_nameservers is not None:
            query['dns_nameservers'] = dns_nameservers
        return super(SubnetManager, self).create(**query)
