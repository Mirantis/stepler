"""
-----------------------------------
Fixtures to manipulate with routers
-----------------------------------
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

from stepler.horizon.steps import RoutersSteps
from stepler.third_party import utils

__all__ = [
    'create_router',
    'router',
    'routers_steps'
]


@pytest.fixture
def routers_steps(setup_network, horizon, login):
    """Fixture to get routers steps."""
    return RoutersSteps(horizon)


@pytest.yield_fixture
def create_router(routers_steps):
    """Fixture to router with options.

    Can be called several times during test.
    """
    routers = []

    def _create_router(router_name):
        routers_steps.create_router(router_name)
        router = utils.AttrDict(name=router_name)
        routers.append(router)
        return router

    yield _create_router

    for router in routers:
        routers_steps.delete_router(router.name)


@pytest.fixture
def router(create_router):
    """Fixture to create router with default options."""
    router_name = next(utils.generate_ids('router'))
    return create_router(router_name)
