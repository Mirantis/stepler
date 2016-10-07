"""
----------------
Routers fixtures
----------------
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
    'add_router_interfaces',
    'create_router',
    'delete_routers_cascade',
    'router',
    'router_steps',
]


@pytest.fixture
def router_steps(neutron_client):
    """Fixture to get router steps."""
    return steps.RouterSteps(neutron_client.routers)


@pytest.yield_fixture
def create_router(router_steps):
    """Fixture to create router with options.

    Can be called several times during a test.
    After the test it destroys all created routers.

    Args:
        router_steps (object): instantiated neutron steps

    Returns:
        function: function to create router as batch with options
    """
    routers = []

    def _create_router(router_name, distributed=False):
        router = router_steps.create(router_name, distributed=distributed)
        routers.append(router)
        return router

    yield _create_router

    for router in routers:
        router_steps.delete(router)


@pytest.yield_fixture
def router(router_steps, create_router, public_network):
    """Fixture to create router with default options before test.

    Args:
        router_steps (object): instantiated neutron steps
        create_router (function): function to create router with options
        public_network (dict): public network

    Returns:
        dict: router
    """
    router_name = next(generate_ids('router'))
    router = create_router(router_name)
    router_steps.set_gateway(router, public_network)
    yield router
    router_steps.clear_gateway(router)


@pytest.yield_fixture
def add_router_interfaces(router_steps):
    """Fixture to add interfaces to router.

    Can be called several times during a test.
    After the test remove added interfaces from router.

    Args:
        router_steps (object): instantiated neutron steps

    Returns:
        function: function to add interfaces to router
    """
    _cleanup_data = []

    def _add_router_interfaces(router, subnets=()):
        _cleanup_data.append([router, subnets])
        for subnet in subnets:
            router_steps.add_subnet_interface(router, subnet)

    yield _add_router_interfaces

    for router, subnets in _cleanup_data:
        for subnet in subnets:
            router_steps.remove_subnet_interface(router, subnet)


@pytest.fixture
def delete_routers_cascade(port_steps, router_steps):
    """Fixture to delete routers cascade."""

    def _delete_routers_cascade(routers):
        for router in routers:
            router_steps.clear_gateway(router)

            for port in port_steps.get_ports(router['id']):
                router_steps.remove_interface(router, port=port)

            router_steps.delete(router)

    return _delete_routers_cascade
