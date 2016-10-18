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

from stepler.baremetal.steps import IronicPortSteps

__all__ = [
    'ironic_port_steps',
    'create_ironic_port'
]

@pytest.fixture
def ironic_port_steps(ironic_client):
    """Fixture to get ironic port steps."""
    return IronicPortSteps(ironic_client)

@pytest.yield_fixture
def create_ironic_port(ironic_port_steps):
    """Fixture to create port with options.

    Can be called several times during test.
    """
    ports = []
    def _create_ironic_port(ironic_node_uuid, address, **kwargs):
        port = ironic_port_steps.create_port(ironic_node_uuid,
                                             address, **kwargs)
        ports.append(port)
        return port

    yield _create_ironic_port

    for port in ports:
        ironic_port_steps.delete_port(port.uuid)


