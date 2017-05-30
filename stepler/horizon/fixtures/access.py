"""
----------------------------------
Fixtures to manipulate with access
----------------------------------
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

from stepler.horizon import steps
from stepler.third_party import utils

__all__ = [
    'access_steps_ui',
    'horizon_create_security_group',
    'horizon_security_group'
]


@pytest.fixture
def access_steps_ui(login, horizon):
    """Fixture to get access steps.

    Args:
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application
    """
    return steps.AccessSteps(horizon)


@pytest.fixture
def horizon_create_security_group(neutron_security_group_steps):
    """Callable function fixture to create security group with options.

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
def horizon_security_group(horizon_create_security_group):
    """Function fixture to create security group before test.

    Args:
    horizon_create_security_group (function): function to create security
        group with options.

    Returns:
        dict: security group
    """
    group_name = next(utils.generate_ids('security-group'))
    group = horizon_create_security_group(group_name)
    return group
