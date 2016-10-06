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

from stepler.third_party.neutron.models import network
from stepler.third_party.neutron.models import port
from stepler.third_party.neutron.models import router
from stepler.third_party.neutron.models import subnet


class NeutronClient(object):
    """Wrapper for python-neutronclient."""
    def __init__(self, client):
        self._client = client
        self.networks = network.NetworkManager(self, client)
        self.ports = port.PortManager(self, client)
        self.routers = router.RouterManager(self, client)
        self.subnets = subnet.SubnetManager(self, client)
