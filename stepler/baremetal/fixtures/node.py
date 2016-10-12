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

from stepler.baremetal.steps import NodeSteps

__all__ = [
    'create_node',
    'node',
    'node_steps'
]


@pytest.fixture
def node_steps(ironic_client):
    """Fixture to get flavor steps."""
    return NodeSteps(ironic_client.node)


@pytest.yield_fixture
def create_node():
    """Fixture to create node with options.

    Can be called several times during test.
    """
    nodes = []

    def _create_node():
        node = node_steps.create_node()
        nodes.append(node)
        return node

    yield _create_node

    for node in nodes:
        node_steps.delete_node(node)


@pytest.fixture
def node(create_node):
    """Fixture to create node with default options before test."""
    return create_node()
