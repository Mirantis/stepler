"""
------------------
Fixtures for users
------------------
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

from stepler.horizon.steps import UsersSteps

from stepler.horizon.config import USER_PROJECT
from stepler.third_party import utils

__all__ = [
    'create_user',
    'create_users',
    'user',
    'users_steps'
]


@pytest.fixture
def users_steps(login, horizon):
    """Fixture to get users steps."""
    return UsersSteps(horizon)


@pytest.yield_fixture
def create_user(users_steps):
    """Callable fixture to create user with options.

    Can be called several times during test.
    """
    users = []

    def _create_user(username, password, project):
        users_steps.create_user(username, password, project)
        user = utils.AttrDict(name=username, password=password)

        users.append(user)
        return user

    yield _create_user

    for user in users:
        users_steps.delete_user(user.name)


@pytest.yield_fixture
def create_users(users_steps):
    """Callable fixture to create users with options.

    Can be called several times during test.
    """
    users = []

    def _create_users(usernames):
        _users = []

        for username in usernames:
            users_steps.create_user(username, username, USER_PROJECT)
            user = utils.AttrDict(name=username, password=username)

            users.append(user)
            _users.append(user)

        return _users

    yield _create_users

    if users:
        users_steps.delete_users([user.name for user in users])


@pytest.fixture
def user(create_user):
    """Fixture to create user with default options before test."""
    username = next(utils.generate_ids('user'))
    return create_user(username, username, USER_PROJECT)
