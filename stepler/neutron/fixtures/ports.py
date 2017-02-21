"""
--------------
Ports fixtures
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

import pytest

from stepler.neutron import steps

__all__ = [
    'create_port',
    'port',
    'port_steps'
]


@pytest.fixture
def port_steps(neutron_client):
    """Fixture to get port steps."""
    return steps.PortSteps(neutron_client.ports)


@pytest.yield_fixture
def create_port(port_steps):
    """Function fixture to create port with options.

    Can be called several times during a test.
    After the test it destroys all created ports.

    Args:
        port_steps (object): instantiated neutron steps

    Returns:
        function: function to create port as batch with options
    """
    ports = []

    def _create_port(network, **kwargs):
        port = port_steps.create(network, **kwargs)
        ports.append(port)
        return port

    yield _create_port

    for port in ports:
        port_steps.delete(port)


@pytest.fixture
def port(network, subnet, create_port):
    """Fixture to create port with default options before test."""
    return create_port(network)
