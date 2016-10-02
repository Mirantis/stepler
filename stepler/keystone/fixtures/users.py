"""
User fixtures.

@author: mshalamov@mirantis.com
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
def admin(user_steps):
    """Fixture to get admin."""
    return user_steps.get_user(name='admin')


@pytest.fixture
def user_steps(keystone_client):
    """Fixture to get user steps."""
    return UserSteps(keystone_client.users)


@pytest.yield_fixture
def create_user(user_steps):
    """Fixture to create user with options.

    Can be called several times during test.
    """
    users = []

    def _create_user(user_name, password):
        user = user_steps.create_user(user_name, password)
        users.append(user)
        return user

    yield _create_user

    for user in users:
        user_steps.delete_user(user)


@pytest.fixture
def user(create_user):
    """Fixture to create user with default options before test."""
    user_name = next(generate_ids('user'))
    password = next(generate_ids('password'))
    return create_user(user_name, password)
