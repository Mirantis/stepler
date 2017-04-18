"""
----------------
Subnets fixtures
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
    'create_subnet',
    'subnet',
    'subnet_steps',
    'get_subnet_steps',
]


@pytest.fixture(scope="session")
def get_subnet_steps(get_neutron_client):
    """Callable session fixture to get router steps.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client

    Returns:
        function: function to get instantiated subnet steps
    """

    def _get_steps(**credentials):
        return steps.SubnetSteps(get_neutron_client(**credentials).subnets)

    return _get_steps


@pytest.fixture
def subnet_steps(get_subnet_steps):
    """Function fixture to get subnet steps.

    Args:
        get_subnet_steps (function): function to get instantiated subnet
            steps

    Returns:
        stepler.neutron.steps.SubnetSteps: instantiated subnet steps
    """
    return get_subnet_steps()


@pytest.yield_fixture
def create_subnet(subnet_steps):
    """Fixture to create subnet with options.

    Can be called several times during a test.
    After the test it destroys all created subnets.

    Args:
        subnet_steps (object): instantiated neutron steps

    Returns:
        function: function to create subnet as batch with options
    """
    subnets = []

    def _create_subnet(subnet_name, network, cidr, project_id=None, **kwargs):
        subnet = subnet_steps.create(subnet_name, network=network, cidr=cidr,
                                     project_id=project_id, **kwargs)
        subnets.append(subnet)
        return subnet

    yield _create_subnet

    for subnet in subnets:
        subnet_steps.delete(subnet)


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
