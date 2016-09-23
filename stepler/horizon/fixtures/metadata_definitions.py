"""
Fixtures for metadata definitions.

@author: schipiga@mirantis.com
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

from stepler.horizon.steps import NamespacesSteps

from stepler.horizon.utils import AttrDict, generate_ids

__all__ = [
    'create_namespace',
    'namespace',
    'namespaces_steps',
]


@pytest.fixture
def namespaces_steps(horizon, login):
    """Fixture to get namespaces steps."""
    return NamespacesSteps(horizon)


@pytest.yield_fixture
def create_namespace(namespaces_steps):
    """Fixture to namespace with options.

    Can be called several times during test.
    """
    namespaces = []

    def _create_namespace(namespace_name):
        namespaces_steps.create_namespace(namespace_name)
        namespace = AttrDict(name=namespace_name)
        namespaces.append(namespace)
        return namespace

    yield _create_namespace

    for namespace in namespaces:
        namespaces_steps.delete_namespace(namespace.name)


@pytest.fixture
def namespace(create_namespace):
    """Fixture to create namespace with default options."""
    namespace_name = next(generate_ids('namespace'))
    return create_namespace(namespace_name)
