"""
---------------------
Fixtures for networks
---------------------
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

from stepler.horizon.steps import NetworksSteps
from stepler.third_party import utils

__all__ = [
    'create_network',
    'create_networks',
    'network',
    'networks_steps'
]


@pytest.fixture
def networks_steps(login, horizon):
    """Fixture to get networks steps."""
    return NetworksSteps(horizon)


@pytest.yield_fixture
def create_networks(networks_steps, horizon):
    """Fixture to create networks with options.

    Can be called several times during test.
    """
    networks = []

    def _create_networks(network_names):
        _networks = []

        for network_name in network_names:
            networks_steps.create_network(network_name)

            network = utils.AttrDict(name=network_name)
            networks.append(network)
            _networks.append(network)

        return _networks

    yield _create_networks

    if networks:
        networks_steps.delete_networks([network.name for network in networks])


@pytest.yield_fixture
def create_network(networks_steps):
    """Fixture to create network with options.

    Can be called several times during test.
    """
    networks = []

    def _create_network(network_name, shared=False):
        networks_steps.create_network(network_name, shared=shared)
        network = utils.AttrDict(name=network_name)
        networks.append(network)
        return network

    yield _create_network

    for network in networks:
        networks_steps.delete_network(network.name)


@pytest.fixture
def network(create_network):
    """Fixture to create network with default options before test."""
    network_name = next(utils.generate_ids('network'))
    return create_network(network_name)
