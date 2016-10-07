"""
-----------------
Port fixtures
-----------------
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

import pytest

from stepler.neutron import steps

__all__ = [
    'delete_ports_cascade',
    'port_steps',
]


@pytest.fixture
def port_steps(neutron_client):
    """Fixture to get port steps."""
    return steps.NetworkSteps(neutron_client.ports)


@pytest.fixture
def delete_ports_cascade(port_steps, router_steps):
    """Fixture to delete ports cascade."""

    def _delete_ports_cascade(ports):
        for port in ports:
            if port['device_owner'] == 'network:router_interface':
                router_steps.remove_interface(port['device_id'],
                                              port['id'])
            port_steps.delete_port(port)

    return _delete_ports_cascade
