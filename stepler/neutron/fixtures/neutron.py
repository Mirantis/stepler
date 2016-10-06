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

__all__ = [
    'create_network',
    'network',
    'public_network',
    'create_subnet',
    'subnet',
    'create_router',
    'router',
    'add_router_interfaces',
    'neutron_client',
    'neutron_steps'
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
    """Fixture to create network with default options before test."""
    network_name = next(generate_ids('network'))
    return create_network(network_name)


@pytest.fixture
def public_network(neutron_steps):
    """Fixture to return public network.

    Args:
        neutron_steps (object): instantiated neutron steps

    Returns:
        dict: public network
    """
    return neutron_steps.get_public_network()


@pytest.yield_fixture
def create_subnet(neutron_steps):
    """Fixture to create subnet with options.

    Can be called several times during a test.
    After the test it destroys all created subnets.

    Args:
        neutron_steps (object): instantiated neutron steps

    Returns:
        function: function to create subnet as batch with options
    """
    subnets = []

    def _create_subnet(subnet_name, network, cidr):
        subnet = neutron_steps.create_subnet(subnet_name, network=network,
                                             cidr=cidr)
        subnets.append(subnet)
        return subnet

    yield _create_subnet

    for subnet in subnets:
        neutron_steps.delete_subnet(subnet)


@pytest.fixture
def subnet(create_subnet, network):
    """Fixture to create subnet with default options before test.

    Args:
        create_subnet (function): function to create subnet with options
        network (dict): network

    Returns:
        dict: subnet
    """
    subnet_name = next(generate_ids('subnet'))
    return create_subnet(subnet_name, network, cidr='10.0.1.0/24')


@pytest.yield_fixture
def create_router(neutron_steps):
    """Fixture to create router with options.

    Can be called several times during a test.
    After the test it destroys all created routers.

    Args:
        neutron_steps (object): instantiated neutron steps

    Returns:
        function: function to create router as batch with options
    """
    routers = []

    def _create_router(router_name, distributed=False):
        router = neutron_steps.create_router(router_name,
                                             distributed=distributed)
        routers.append(router)
        return router

    yield _create_router

    for router in routers:
        neutron_steps.delete_router(router)


@pytest.yield_fixture
def router(neutron_steps, create_router, public_network):
    """Fixture to create router with default options before test.

    Args:
        create_router (function): function to create router with options
        public_network (dict): public network

    Returns:
        dict: router
    """
    router_name = next(generate_ids('router'))
    router = create_router(router_name)
    neutron_steps.set_router_gateway(router, public_network)
    yield router
    neutron_steps.clear_router_gateway(router)


@pytest.yield_fixture
def add_router_interfaces(neutron_steps):
    """Fixture to add interfaces to router.

    Can be called several times during a test.
    After the test remove added interfaces from router.

    Args:
        neutron_steps (object): instantiated neutron steps

    Returns:
        function: function to add interfaces to router
    """
    _cleanup_data = []

    def _add_router_interfaces(router, subnets=()):
        _cleanup_data.append([router, subnets])
        for subnet in subnets:
            neutron_steps.add_router_subnet_interface(router, subnet)

    yield _add_router_interfaces

    for router, subnets in _cleanup_data:
        for subnet in subnets:
            neutron_steps.remove_router_subnet_interface(router, subnet)
