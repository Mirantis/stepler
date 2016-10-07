"""
----------
Port steps
----------
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

import waiting

from stepler import base
from stepler.third_party import steps_checker

__all__ = ["PortSteps"]


class PortSteps(base.BaseSteps):
    """Port steps."""

    @steps_checker.step
    def get_network_id_by_mac(self, mac):
        """Step to get network ID by server MAC.

        Args:
            mac (string): mac address
        Returns:
            string: network ID
        """
        # TODO(schipiga): it should return data structure, not value of key.
        return self._client.find_all(mac_address=mac)[0]['network_id']

    def get_ports(self, subnet_id=None, router_id=None):
        """Return ports with interface to subnet or router."""
        if subnet_id:
            ports = []
            for port in self._client.list():
                for fixed_ip in port['fixed_ips']:
                    if fixed_ip['subnet_id'] == subnet_id:
                        ports.append(port)
            return ports

        if router_id:
            return self._client.find_all(
                device_owner='network:router_interface',
                device_id=router_id)

        return self._client.list()
