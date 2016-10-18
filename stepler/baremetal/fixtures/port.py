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

from stepler.baremetal import steps
from stepler.third_party import utils

__all__ = [
    'ironic_port_steps',
    'ironic_port'
]


@pytest.fixture
def ironic_port_steps(ironic_client):
    """Fixture to get ironic port steps.

    Args:
        ironic_client (object): instantiated ironic client

    Returns:
        stepler.baremetal.steps.IronicPortSteps: instantiated ironic port step
    """
    return steps.IronicPortSteps(ironic_client)


@pytest.fixture
def ironic_port(ironic_node, ironic_port_steps):
    """Fixture to create ironic port with default options before test.

    Args:
        ironic_node (object): ironic node of the ports
        should be associated with

    Returns:
        (object): ironic port
    """
    mac_address = next(utils.generate_mac_addresses())
    return ironic_port_steps.create_port(mac_address, ironic_node)
