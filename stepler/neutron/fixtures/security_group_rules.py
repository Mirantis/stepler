"""
-------------------------------------
Neutron security group rules fixtures
-------------------------------------
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
    'get_neutron_security_group_rule_steps',
    'neutron_security_group_rule_steps',
]


@pytest.fixture(scope="session")
def get_neutron_security_group_rule_steps(get_neutron_client):
    """Callable session fixture to get security group rules steps.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client

    Returns:
        function: function to get instantiated security group rules steps
    """

    def _get_steps(**credentials):
        return steps.NeutronSecurityGroupRuleSteps(
            get_neutron_client(**credentials).security_group_rules)

    return _get_steps


@pytest.fixture
def neutron_security_group_rule_steps(get_neutron_security_group_rule_steps):
    """Function fixture to get security group rule steps.

    Args:
        get_neutron_security_group_rule_steps (function): function to get
            instantiated security group rules steps

    Returns:
        stepler.neutron.steps.NeutronSecurityGroupRuleSteps: instantiated
            security group rules steps
    """
    return get_neutron_security_group_rule_steps()
