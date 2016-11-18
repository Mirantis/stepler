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
    'create_router',
    'router',
    'add_router_interfaces',
    'router_steps',
    'get_router_steps',
]


@pytest.fixture(scope="session")
def get_router_steps(get_neutron_client):
    """Callable session fixture to get router steps.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client

    Returns:
        function: function to get instantiated router steps
    """

    def _get_steps(**credentials):
        return steps.RouterSteps(get_neutron_client(**credentials).routers)

    return _get_steps


@pytest.fixture
def router_steps(get_router_steps):
    """Function fixture to get router steps.

    Args:
        get_router_steps (function): function to get instantiated router
            steps

    Returns:
        stepler.neutron.steps.RouterSteps: instantiated router steps
    """
    return get_router_steps()


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
def router(request, router_steps, create_router, public_network):
    """Fixture to create router with default options before test.

    Args:
        request (obj): py.test SubRequest
        router_steps (object): instantiated neutron steps
        create_router (function): function to create router with options
        public_network (dict): public network

    Returns:
        dict: router
    """
    router_params = dict(distributed=False)
    router_params.update(getattr(request, 'param', {}))
    router_name = next(generate_ids('router'))
    router = create_router(router_name, **router_params)
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
