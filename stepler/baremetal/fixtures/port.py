"""
--------------------
Ironic port fixtures
--------------------
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

from stepler.baremetal import steps

__all__ = [
    'get_ironic_port_steps',
    'ironic_port_steps',
    'ironic_port'
]


@pytest.fixture(scope='session')
def get_ironic_port_steps(get_ironic_client):
    """Callable session fixture to get ironic port steps.

    Args:

        get_ironic_client (function): function to get ironic client

    Returns:
        function: function to get ironic port steps
    """
    def _get_ironic_port_steps(**credentials):
        return steps.IronicPortSteps(
            get_ironic_client(**credentials))

    return _get_ironic_port_steps


@pytest.fixture
def ironic_port_steps(get_ironic_port_steps):
    """Callable function fixture to get ironic steps.

    Can be called several times during a test.
    After the test it destroys all created ports.

    Args:
        get_ironic_port_steps (function): function to get ironic steps

    Returns:
        IronicPortSteps: instantiated ironic port steps
    """
    return get_ironic_port_steps()


@pytest.fixture
def ironic_port(ironic_node, ironic_port_steps):
    """Fixture to create ironic port with default options before test.

    Args:
        ironic_node (object): ironic node of the ports
            should be associated with

    Returns:
        (object): ironic port
    """
    return ironic_port_steps.create_port(ironic_node)
