"""
-------------
Role fixtures
-------------
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

from stepler.keystone import steps
from stepler.third_party.utils import generate_ids

__all__ = [
    'admin_role',
    'create_role',
    'get_role_steps',
    'role_steps',
    'role'
]


@pytest.fixture
def admin_role(role_steps):
    """Fixture to get admin role."""
    return role_steps.get_role(name='admin')


@pytest.fixture(scope="session")
def get_role_steps(get_keystone_client):
    """Callable session fixture to get role steps.

    Args:
        get_keystone_client (function): function to get keystone client.

    Returns:
        function: function to get role steps.
    """
    def _get_steps():
        return steps.RoleSteps(get_keystone_client().roles)

    return _get_steps


@pytest.fixture
def role_steps(get_role_steps):
    """Function fixture to get role steps.

    Args:
        get_role_steps (function): function to get role steps

    Returns:
        RoleSteps: instantiated role steps.
    """
    return get_role_steps()


@pytest.yield_fixture
def create_role(role_steps):
    """Fixture to create role with options.

    Can be called several times during test.
    """
    roles = []

    def _create_role(role_name):
        role = role_steps.create_role(role_name)
        roles.append(role)
        return role

    yield _create_role

    for role in roles:
        role_steps.delete_role(role)


@pytest.fixture
def role(create_role):
    """Fixture to create role with default options before test."""
    role_name = next(generate_ids('role'))
    return create_role(role_name)
