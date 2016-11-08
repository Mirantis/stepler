"""
-----------------
Networks fixtures
-----------------
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

from stepler import config
from stepler.neutron import steps
from stepler.third_party.utils import generate_ids

__all__ = [
    'create_network',
    'network',
    'public_network',
    'network_steps',
    'get_network_steps',
    'admin_internal_network',
    'internal_network'
]


@pytest.fixture(scope="session")
def get_network_steps(get_neutron_client):
    """Callable session fixture to get network steps.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client

    Returns:
        function: function to get instantiated network steps
    """
    def _get_steps(**credentials):
        return steps.NetworkSteps(get_neutron_client(**credentials).networks)

    return _get_steps


@pytest.fixture
def network_steps(get_network_steps):
    """Function fixture to get network steps.

    Args:
        get_network_steps (function): function to get instantiated network
            steps

    Returns:
        stepler.neutron.steps.NetworkSteps: instantiated network steps
    """
    return get_network_steps()


@pytest.yield_fixture
def create_network(network_steps):
    """Callable fixture to create network with default options.

    Can be called several times during test.

    Args:
        network_steps (object): instantiated network steps

    Yields:
        function: function to create network with default options
    """
    networks = []

    def _create_network(network_name):
        network = network_steps.create(network_name)
        networks.append(network)
        return network

    yield _create_network

    for network in networks:
        network_steps.delete(network)


@pytest.fixture
def network(create_network):
    """Function fixture to create network with default options before test.

    Args:
        create_network (function): function to create network

    Returns:
        object: network
    """
    network_name = next(generate_ids('network'))
    return create_network(network_name)


@pytest.fixture
def public_network(network_steps):
    """Function fixture to return public network.

    Args:
        network_steps (object): instantiated network steps

    Returns:
        dict: public network
    """
    params = {'router:external': True, 'status': 'ACTIVE'}
    return network_steps.get_network(**params)


@pytest.fixture
def internal_network(network_steps):
    """Fixture returns internal network.

    Args:
        network_steps (object): instantiated network steps

    Returns:
        dict: internal network
    """
    params = {'router:external': False, 'status': 'ACTIVE'}
    return network_steps.get_network(**params)


@pytest.fixture
def admin_internal_network(network_steps):
    """Function fixture to find admin internal network before test.

    Args:
        network_steps (object): instantiated network steps

    Returns:
        object: admin internal network
    """
    return network_steps.get_network_by_name(
        name=config.ADMIN_INTERNAL_NETWORK_NAME)
