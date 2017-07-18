"""
----------------------
Fixtures for instances
----------------------
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
from stepler.horizon import steps

__all__ = [
    'instances_steps_ui',
    'horizon_servers',
    'horizon_server',
]


@pytest.fixture
def instances_steps_ui(network_setup, server_steps, login, horizon):
    """Function fixture to get instances steps.

    server_steps instance is used for servers cleanup.

    Args:
        network_setup (None): should set up network before steps using
        server_steps (ServerSteps): instantiated server steps
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.InstancesSteps: instantiated instances steps
    """
    return steps.InstancesSteps(horizon)


@pytest.fixture
def horizon_servers(request,
                    cirros_image,
                    security_group,
                    net_subnet_router,
                    flavor_steps,
                    server_steps):
    """Function fixture to create servers with default options before test.

    Args:
        request (object): py.test's SubRequest instance
        cirros_image (object): cirros image from glance
        security_group (object): nova security group
        net_subnet_router (tuple): neutron network, subnet, router
        flavor_steps (FlavorSteps): instantiated flavor steps
        server_steps (ServerSteps): instantiated server steps

    Returns:
        list: nova servers
    """
    count = int(getattr(request, 'param', 3))
    network, _, _ = net_subnet_router
    flavor = flavor_steps.get_flavor(name=config.HORIZON_TEST_FLAVOR_TINY)
    return server_steps.create_servers(image=cirros_image,
                                       flavor=flavor,
                                       count=count,
                                       networks=[network],
                                       security_groups=[security_group],
                                       username=config.CIRROS_USERNAME,
                                       password=config.CIRROS_PASSWORD)


@pytest.fixture
@pytest.mark.parametrize('horizon_servers', [1])
def horizon_server(horizon_servers):
    """Function fixture to create server with default options before test.

    Args:
        horizon_servers (list): list with one nova server

    Returns:
        object: nova server
    """
    return horizon_servers[0]
