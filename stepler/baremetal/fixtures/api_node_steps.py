"""
---------------
Ironic fixtures
---------------
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

import logging

import pytest

from stepler import config
from stepler.baremetal import steps

__all__ = [
    'get_ironic_steps',
    'ironic_steps_v1',
    'api_ironic_steps_v1',
    'api_ironic_steps',
]

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def get_ironic_steps(request, get_ironic_client):
    """Callable session fixture to get ironic steps.

    Args:
        get_ironic_client (function): function to get ironic client

    Returns:
        function: function to get ironic steps
    """
    def _get_ironic_steps(version, is_api):
        ironic_client = get_ironic_client(version, is_api)

        ironic_steps_cls = {'1': steps.NodeApiClientV1}[version]

        return ironic_steps_cls(ironic_client)

    return _get_ironic_steps


@pytest.fixture
def ironic_steps_v1(get_ironic_steps):
    """Function fixture to get ironic steps for v1.

    Args:
        get_ironic_steps (function): function to get ironic steps

    Returns:
        ironicStepsV1: instantiated ironic steps v1
    """
    return get_ironic_steps(version='1', is_api=False)


@pytest.fixture
def api_ironic_steps_v1(get_ironic_steps):
    """Function fixture to get API ironic steps for v1.

    Args:
        get_ironic_steps (function): function to get ironic steps

    Returns:
        ironicStepsV1: instantiated ironic steps v1
    """
    return get_ironic_steps(version='1', is_api=True)


@pytest.fixture
def ironic_steps(get_ironic_steps, nodes_cleanup):
    """Function fixture to get API ironic steps.

    Args:
        get_ironic_steps (function): function to get ironic steps
        nodes_cleanup (function): function to cleanup nodes after test

    Yields:
        object: instantiated ironic steps of current version
    """
    _ironic_steps = get_ironic_steps(
        version=config.CURRENT_IRONIC_VERSION, is_api=False)

    with nodes_cleanup(_ironic_steps):
        yield _ironic_steps


@pytest.fixture
def api_ironic_steps(get_ironic_steps):
    """Function fixture to get API ironic steps.

    Args:
        get_ironic_steps (function): function to get API ironic steps

    Returns:
        ironicSteps: instantiated ironic steps
    """
    return get_ironic_steps(
        version=config.CURRENT_IRONIC_VERSION, is_api=True)