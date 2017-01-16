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


__all__ = [
    'get_neutron_security_group_steps',
    'neutron_security_group_steps',
    'neutron_security_groups_cleanup',
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
