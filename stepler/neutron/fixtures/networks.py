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

from stepler.neutron import steps
from stepler.third_party.utils import generate_ids

__all__ = [
    'create_network',
    'network',
    'public_network',
    'network_steps'
]


@pytest.fixture
def network_steps(neutron_client):
    """Fixture to get network steps."""
    return steps.NetworkSteps(neutron_client.networks)


@pytest.yield_fixture
def create_network(network_steps):
    """Fixture to create network with options.

    Can be called several times during test.
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
    """Fixture to create network with default options before test."""
    network_name = next(generate_ids('network'))
    return create_network(network_name)


@pytest.fixture
def public_network(network_steps):
    """Fixture to return public network.

    Args:
        network_steps (object): instantiated neutron steps

    Returns:
        dict: public network
    """
    return network_steps.get_public_network()


@pytest.fixture
def cascade_delete_networks(network_steps, subnet_steps, port_steps,
                            router_steps):
    """Fixture to cascade delete networks."""

    def _cascade_delete_networks(networks):
        for network in networks:
            for subnet_id in network['subnets']:
                port_ids = port_steps.get_ports(subnet_id)

                for port_id in port_ids:
                    router_steps.remove_port_interface(port_id)

                    port_steps.delete_port(port_id)
                subnet_steps.delete_subnet(subnet_id)
            network_steps.delete_network(network)

    return _cascade_delete_networks
