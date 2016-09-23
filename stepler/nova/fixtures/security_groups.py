"""
Security group fixtures.

@author: schipiga@mirantis.com
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

from stepler.nova.steps import SecurityGroupSteps
from stepler.utils import generate_ids

__all__ = [
    'create_security_group',
    'security_group',
    'security_group_steps'
]


@pytest.fixture
def security_group_steps(nova_client):
    """Fixture to get security group steps."""
    return SecurityGroupSteps(nova_client)


@pytest.yield_fixture
def create_security_group(security_group_steps):
    """Fixture to create security group with options.

    Can be called several times during test.
    """
    security_groups = []

    def _create_security_group(group_name):
        security_group = security_group_steps.create_group(group_name)
        security_groups.append(security_group)
        return security_group

    yield _create_security_group

    for security_group in security_groups:
        security_group_steps.delete_group(security_group)


@pytest.fixture
def security_group(create_security_group, security_group_steps):
    """Fixture to create security group with default options before test."""
    group_name = next(generate_ids('security-group'))
    group = create_security_group(group_name)

    rules = [
        {
            # ssh
            'ip_protocol': 'tcp',
            'from_port': 22,
            'to_port': 22,
            'cidr': '0.0.0.0/0',
        },
        {
            # ping
            'ip_protocol': 'icmp',
            'from_port': -1,
            'to_port': -1,
            'cidr': '0.0.0.0/0',
        }
    ]
    security_group_steps.add_group_rules(group, rules)

    return group
