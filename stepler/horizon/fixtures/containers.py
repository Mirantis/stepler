"""
-----------------------
Fixtures for containers
-----------------------
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

from stepler.horizon import steps
from stepler.third_party import utils

__all__ = [
    'create_container_ui',
    'containers_steps_ui',
    'container',
]


@pytest.fixture
def containers_steps_ui(login, horizon):
    """Fixture to get containers steps.

    Args:
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.ContainersSteps: instantiated containers steps
    """
    return steps.ContainersSteps(horizon)


@pytest.fixture
def create_container_ui(containers_steps_ui):
    """Callable fixture to create container with options.

    Can be called several times during test.

    Args:
        containers_steps_ui (obj): instantiated containers steps

    Yields:
        function: function to create container with options
    """
    containers = []

    def _create_container(container_name, public=False):
        containers_steps_ui.create_container(container_name, public=public)
        container = utils.AttrDict(name=container_name)
        containers.append(container)
        return container

    yield _create_container

    for container in containers:
        containers_steps_ui.delete_container(container.name)


@pytest.fixture
def container(create_container_ui):
    """Fixture to create container with default options before test.

    Args:
        create_container_ui (function): function to create container
        with options

    Returns:
        AttrDict: dict with container name
    """
    container_name = next(utils.generate_ids('container'))
    return create_container_ui(container_name)
