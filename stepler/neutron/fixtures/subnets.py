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
    'subnet_steps'
]


@pytest.fixture
def subnet_steps(neutron_client):
    """Fixture to get subnet steps."""
    return steps.SubnetSteps(neutron_client.subnets)


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

    def _create_subnet(subnet_name, network, cidr):
        subnet = subnet_steps.create(subnet_name, network=network, cidr=cidr)
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
