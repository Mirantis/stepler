"""
Fixtures for containers.

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

from stepler.horizon.steps import ContainersSteps

from stepler.horizon.utils import AttrDict, generate_ids  # noqa

__all__ = [
    'create_container',
    'container',
    'containers_steps'
]


@pytest.fixture
def containers_steps(login, horizon):
    """Fixture to get containers steps."""
    return ContainersSteps(horizon)


@pytest.yield_fixture
def create_container(containers_steps):
    """Fixture to create container with options.

    Can be called several times during test.
    """
    containers = []

    def _create_container(container_name, public=False):
        containers_steps.create_container(container_name, public=public)
        container = AttrDict(name=container_name)
        containers.append(container)
        return container

    yield _create_container

    for container in containers:
        containers_steps.delete_container(container.name)


@pytest.fixture
def container(create_container):
    """Fixture to create container with default options before test."""
    container_name = next(generate_ids('container'))
    return create_container(container_name)
