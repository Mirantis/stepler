"""
--------------
Security group
--------------
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
from stepler.nova import steps
from stepler.third_party import utils

__all__ = [
    'create_security_group',
    'security_group',
    'security_group_steps',
    'get_security_group_steps',
]


@pytest.fixture(scope='session')
def get_security_group_steps(get_nova_client):
    """Callable session fixture to get security groups steps.

    Args:
        get_nova_client (function): function to get nova client.

    Returns:
        function: function to get security groups steps.
    """
    def _get_security_group_steps(**credentials):
        return steps.SecurityGroupSteps(get_nova_client(**credentials))

    return _get_security_group_steps


@pytest.fixture
def security_group_steps(get_security_group_steps):
    """Fixture to get security group steps.

    Args:
        get_security_group_steps (function): function to get security groups
            steps
    """
    return get_security_group_steps()


@pytest.yield_fixture
def create_security_group(security_group_steps):
    """Callable function fixture to create security group with options.

    Can be called several times during test.
    After the test it destroys all created security groups

    Args:
        security_group_steps (object): instantiated security groups steps

    Returns:
        function: function to create security group
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
    """Function fixture to create security group before test.

    Can be called several times during test.
    After the test it destroys all created security groups

    Args:
        create_security_group (object): instantiated security group
        security_group_steps (object): instantiated security groups steps

    Returns:
        object: security group
    """
    group_name = next(utils.generate_ids('security-group'))
    group = create_security_group(group_name)

    security_group_steps.add_group_rules(group,
                                         config.SECURITY_GROUP_SSH_PING_RULES)

    return group
