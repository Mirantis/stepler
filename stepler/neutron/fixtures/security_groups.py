"""
------------------------
Security groups fixtures
------------------------
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
from stepler.third_party import utils


__all__ = [
    'get_neutron_security_group_steps',
    'neutron_security_group_steps',
    'neutron_create_security_group',
    'neutron_security_group',
]


@pytest.fixture(scope="session")
def get_neutron_security_group_steps(get_neutron_client):
    """Callable session fixture to get neutron security group steps.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client

    Returns:
        function: function to get instantiated  neutron security group steps
    """

    def _get_steps(**credentials):
        return steps.NeutronSecurityGroupSteps(
            get_neutron_client(**credentials).security_groups)

    return _get_steps


@pytest.fixture
def neutron_security_group_steps(get_neutron_security_group_steps):
    """Function fixture to get neutron security group steps.

    Args:
        get_neutron_security_group_steps (function): function to get
            instantiated neutron security group steps

    Returns:
        stepler.neutron.steps.NeutronSecurityGroupSteps: instantiated neutron
            security group steps
    """
    return get_neutron_security_group_steps()


@pytest.fixture
def neutron_create_security_group(neutron_security_group_steps):
    """Fixture to create security group.

    Can be called several times during a test.
    After the test it destroys all created security groups.

    Args:
        neutron_security_group_steps (object): instantiated neutron security
            group steps

    Returns:
        function: function to create security group as batch with options
    """
    security_groups = []

    def _create_security_group(name, **kwargs):
        security_group = neutron_security_group_steps.create(group_name=name,
                                                             description='')
        security_groups.append(security_group)
        return security_group

    yield _create_security_group

    for security_group in security_groups:
        neutron_security_group_steps.delete(security_group)


@pytest.fixture
def neutron_security_group(create_security_group):
    """Fixture to create security group with default options before test.

    Args:
        create_security_group (function): function to create security group
            with options

    Returns:
        object: security group
    """
    return create_security_group(next(utils.generate_ids()))
