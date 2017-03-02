"""
--------------------------------
Neutron security groups fixtures
--------------------------------
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
from stepler.neutron import steps
from stepler.third_party import utils


__all__ = [
    'get_neutron_security_group_steps',
    'neutron_security_group_steps',
    'neutron_security_groups_cleanup',
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
        function: function to get instantiated neutron security group steps
    """

    def _get_steps(**credentials):
        return steps.NeutronSecurityGroupSteps(
            get_neutron_client(**credentials).security_groups)

    return _get_steps


@pytest.fixture
def neutron_security_group_steps(get_neutron_security_group_steps,
                                 neutron_security_groups_cleanup):
    """Function fixture to get neutron security group steps.

    Args:
        get_neutron_security_group_steps (function): function to get
            instantiated neutron security group steps
        neutron_security_groups_cleanup (function): function to cleanup
            created security groups

    Returns:
        stepler.neutron.steps.NeutronSecurityGroupSteps: instantiated neutron
            security group steps
    """
    return get_neutron_security_group_steps()


@pytest.fixture
def neutron_security_groups_cleanup(get_neutron_security_group_steps):
    """Function fixture to cleanup security groups after test.

    Args:
        get_neutron_security_group_steps (function): function to get
            instantiated neutron security group steps
    """
    security_group_steps = get_neutron_security_group_steps()
    groups_before = security_group_steps.get_security_groups(check=False)
    group_ids_before = [group['id'] for group in groups_before]

    yield

    groups = security_group_steps.get_security_groups(check=False)
    for group in groups:
        if group['id'] not in group_ids_before:
            security_group_steps.delete(group)


@pytest.fixture
def neutron_create_security_group(neutron_security_group_steps):
    """Callable function fixture to create security group with options.

    Can be called several times during test.
    After the test it destroys all created security groups

    Args:
        neutron_security_group_steps (object): instantiated security groups
            steps

    Returns:
        function: function to create security group
    """
    security_groups = []

    def _create_security_group(group_name, **kwargs):
        security_group = neutron_security_group_steps.create(group_name,
                                                             **kwargs)
        security_groups.append(security_group)
        return security_group

    yield _create_security_group

    for security_group in security_groups:
        neutron_security_group_steps.delete(security_group)


@pytest.fixture
def neutron_security_group(neutron_create_security_group,
                           neutron_security_group_rule_steps):
    """Function fixture to create security group before test.

    Can be called several times during test.
    After the test it destroys all created security groups

    Args:
        neutron_create_security_group (function): function to create security
            group with options
        neutron_security_group_rule_steps (object): instantiated security
            groups rules steps

    Returns:
        dict: security group
    """
    group_name = next(utils.generate_ids('security-group'))
    group = neutron_create_security_group(group_name)

    neutron_security_group_rule_steps.add_rules_to_group(
        group['id'], config.SECURITY_GROUP_SSH_PING_RULES)

    return group
