"""
-------------
User fixtures
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

from stepler.keystone.steps import UserSteps
from stepler.third_party.utils import generate_ids

__all__ = [
    'admin',
    'create_user',
    'user_steps',
    'user'
]


@pytest.fixture
def user_steps(keystone_client):
    """Fixture to get user steps.

    Args:
        keystone_client (object): instantiated keystone client

    Returns:
        stepler.keystone.steps.UserSteps: instantiated user steps
    """
    return UserSteps(keystone_client.users)


@pytest.fixture
def admin(user_steps):
    """Fixture to get admin.

    Args:
        user_steps (object): instantiated user steps

    Returns:
        object: user 'admin'
    """
    return user_steps.get_user(name='admin')


@pytest.yield_fixture
def create_user(user_steps):
    """Fixture to create user with options.

    Can be called several times during a test.
    After the test it destroys all created users.

    Args:
        user_steps (object): instantiated user steps

    Yields:
        function: function to create user with options
    """
    users = []

    def _create_user(user_name, password, *args, **kwgs):
        user = user_steps.create_user(user_name, password, *args, **kwgs)
        users.append(user)
        return user

    yield _create_user

    for user in users:
        user_steps.delete_user(user)


@pytest.fixture
def user(create_user):
    """Fixture to create user with default options before test.

    Args:
        create_user (function): function to create user with options

    Returns:
        object: user
    """
    user_name = next(generate_ids('user'))
    password = next(generate_ids('password'))
    return create_user(user_name, password)
