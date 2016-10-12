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

from stepler.baremetal.steps import IronicNodeSteps

__all__ = [
    'create_ironic_node',
    'ironic_node',
    'ironic_node_steps'
]


@pytest.fixture
def ironic_node_steps(ironic_client):
    """Callable session fixture to get ironic steps.

    Args:
        ironic_client (function): function to get glance client

    Returns:
        function: function to instantiated ironic steps
    """
    return IronicNodeSteps(ironic_client)


@pytest.yield_fixture
def create_ironic_node(ironic_node_steps):
    """Callable function fixture to create ironic node with options.

    Can be called several times during a test.
    After the test it destroys all created nodes.

    Args:
        ironic_node_steps (object): instantiated ironic steps

    Returns:
        function: function to create nodes as batch with options
    """
    nodes = []

    def _create_ironic_node():
        node = ironic_node_steps.create_ironic_node()
        nodes.append(node)
        return node

    yield _create_ironic_node

    for node in nodes:
        ironic_node_steps.delete_ironic_node(node)


@pytest.fixture
def ironic_node(create_ironic_node):
    """Callable function fixture to create single ironic node with options.

    Can be called several times during a test.
    After the test it destroys all created nodes.

    Args:
        create_ironic_node (function): function to create nodes with options

    Returns:
        function: function to create single node with options
    """
    return create_ironic_node()
