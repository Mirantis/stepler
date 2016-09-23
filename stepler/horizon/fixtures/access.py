"""
Fixtures to manipulate with access.

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

from stepler.horizon.steps import AccessSteps

from stepler.horizon.utils import AttrDict, generate_ids

__all__ = [
    'access_steps',
    'create_security_group',
    'security_group'
]


@pytest.fixture
def access_steps(horizon, login):
    """Fixture to get access steps."""
    return AccessSteps(horizon)


@pytest.yield_fixture
def create_security_group(access_steps):
    """Fixture to create security group with options.

    Can be called several times during test.
    """
    security_groups = []

    def _create_security_group(group_name):
        access_steps.create_security_group(group_name)
        security_group = AttrDict(name=group_name)
        security_groups.append(security_group)
        return security_group

    yield _create_security_group

    for security_group in security_groups:
        access_steps.delete_security_group(security_group.name)


@pytest.fixture
def security_group(create_security_group):
    """Fixture to create security group with default options."""
    group_name = next(generate_ids('security-group'))
    return create_security_group(group_name)
