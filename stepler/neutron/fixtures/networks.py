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
    'baremetal_network',
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
def network_steps(get_network_steps, uncleanable):
    """Function fixture to get network steps.

    Args:
        get_network_steps (function): function to get instantiated network
            steps
        uncleanable (AttrDict): data structure with skipped resources

    Yields:
        stepler.neutron.steps.NetworkSteps: instantiated network steps
    """
    _network_steps = get_network_steps()

    networks = _network_steps.get_networks(check=False)
    network_ids_before = {network['id'] for network in networks}

    yield _network_steps

    uncleanable_ids = network_ids_before | uncleanable.network_ids
    _cleanup_networks(_network_steps, uncleanable_ids=uncleanable_ids)


def _cleanup_networks(_network_steps, uncleanable_ids=None):
    """Function to cleanup networks.

    Args:
        _network_steps (object): instantiated network steps
        uncleanable_ids (AttrDict): resources ids to skip cleanup
    """
    uncleanable_ids = uncleanable_ids or []

    for network in _network_steps.get_networks(check=False):
        if (network['id'] not in uncleanable_ids and
                network['status'] != config.STATUS_DELETING):
            _network_steps.delete(network)


@pytest.fixture
def create_network(network_steps):
    """Callable fixture to create network with default options.

    Can be called several times during test.

    Args:
        network_steps (object): instantiated network steps

    Yields:
        function: function to create network with default options
    """
    networks = []

    def _create_network(network_name, *args, **kwargs):
        network = network_steps.create(network_name, *args, **kwargs)
        networks.append(network)
        return network

    yield _create_network

    for network in networks:
        network_steps.delete(network)


@pytest.fixture
def network(network_steps):
    """Function fixture to create network with default options before test.

    Args:
        network_steps (object): instantiated network steps

    Returns:
        object: network
    """
    network_name = next(generate_ids('network'))
    return network_steps.create(network_name)


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
def baremetal_network(network_steps):
    """Function fixture to find baremetal network before test.

     Args:
         network_steps (object): instantiated network steps

    Returns:
        object: baremetal network
    """
    return network_steps.get_network_by_name(name=config.BAREMETAL_NETWORK)
