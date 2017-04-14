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

from stepler import config
from stepler.horizon import steps

__all__ = [
    'users_steps_ui',
    'new_user_login',
]


@pytest.fixture
def users_steps_ui(login, horizon):
    """Fixture to get users steps.

    Args:
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.UsersSteps: instantiated users steps
    """
    return steps.UsersSteps(horizon)


@pytest.fixture
def new_user_login(login, new_user_with_project, auth_steps):
    """Fixture to log in as new user.

    Args:
        login (None): should log in horizon before steps using
        new_user_with_project (AttrDict): dict with username, password
            and project name
        auth_steps (AuthSteps): instantiated auth steps

    Yields:
        AttrDict: dict with username, password and project name
    """
    auth_steps.logout()
    auth_steps.login(new_user_with_project.username,
                     new_user_with_project.password)

    yield new_user_with_project

    auth_steps.logout()
    auth_steps.login(config.ADMIN_NAME, config.ADMIN_PASSWD)
