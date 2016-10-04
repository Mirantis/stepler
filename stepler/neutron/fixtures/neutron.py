"""
Neutron fixtures.

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

from neutronclient.v2_0.client import Client
import pytest

from stepler.neutron.steps import NeutronSteps
from stepler.third_party.utils import generate_ids
from stepler import config

__all__ = [
    'create_network',
    'network',
    'neutron_client',
    'neutron_steps',
    'admin_network'
]


@pytest.fixture
def neutron_client(session):
    """Fixture to get nova client."""
    return Client(session=session)


@pytest.fixture
def neutron_steps(neutron_client):
    """Fixture to get neutron steps."""
    return NeutronSteps(neutron_client)


@pytest.yield_fixture
def create_network(neutron_steps):
    """Fixture to create network with options.

    Can be called several times during test.
    """
    networks = []

    def _create_network(network_name):
        network = neutron_steps.create_network(network_name)
        networks.append(network)
        return network

    yield _create_network

    for network in networks:
        neutron_steps.delete_network(network)


@pytest.fixture
def network(create_network):
    """Fixture to create neutron with default options before test."""
    network_name = next(generate_ids('network'))
    return create_network(network_name)


@pytest.fixture
def admin_network(neutron_steps):
    """
    Function fixture to find admin network before test.

    Args:
        neutron_steps (object): instantiated neutron steps

    Returns:
        object: admin network
    """
    return neutron_steps.get_network(name=config.ADMIN_NETWORK_NAME)
