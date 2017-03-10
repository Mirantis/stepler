"""
-----------------------------------------------------
Fixtures to run horizon, login, create demo user, etc
-----------------------------------------------------
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

from stepler.horizon.app import Horizon
from stepler.horizon.steps import AuthSteps

from stepler import config

__all__ = [
    'auth_steps',
    'horizon',
    'login'
]


@pytest.fixture(scope="module")
def horizon():
    """Function fixture to launch browser and open horizon page.

    It launches browser before tests and closes after.

    Yields:
        Horizon: Instantiated horizon web application.
    """
    app = Horizon(config.OS_DASHBOARD_URL)
    yield app
    app.quit()


@pytest.fixture
def auth_steps(horizon):
    """Function fixture to get auth steps.

    Args:
        horizon (object): Instantiated horizon web application.

    Returns:
        AuthSteps: instantiated auth steps.
    """
    return AuthSteps(horizon)


@pytest.fixture
def login(auth_steps, credentials):
    """Function fixture to log in horizon.

    Logs in horizon UI before test.
    Logs out after test.

    Args:
        auth_steps (AuthSteps): instantiated auth steps.
    """
    auth_steps.login(credentials.username, credentials.password)
    auth_steps.switch_project(credentials.project_name)
    yield
    # reload page to be sure that modal form doesn't prevent to logout
    auth_steps.app.current_page.refresh()
    auth_steps.logout()
