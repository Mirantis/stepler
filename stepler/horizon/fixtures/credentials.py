"""
------------------------
Fixtures for credentials
------------------------
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

__all__ = [
    'admin_only',
    'any_one',
    'user_only'
]


@pytest.fixture(params=('admin', 'user'), scope="session")
def any_one(request):
    """Define user to log in account."""
    if request.param == 'admin':
        config.CURRENT_UI_USERNAME = config.ADMIN_NAME
        config.CURRENT_UI_PASSWORD = config.ADMIN_PASSWD
        config.CURRENT_UI_PROJECT_NAME = config.ADMIN_PROJECT
    if request.param == 'user':
        config.CURRENT_UI_USERNAME = config.USER_NAME
        config.CURRENT_UI_PASSWORD = config.USER_PASSWD
        config.CURRENT_UI_PROJECT_NAME = config.USER_PROJECT


@pytest.fixture
def admin_only():
    """Set admin credentials for test."""
    config.CURRENT_UI_USERNAME = config.ADMIN_NAME
    config.CURRENT_UI_PASSWORD = config.ADMIN_PASSWD
    config.CURRENT_UI_PROJECT_NAME = config.ADMIN_PROJECT


@pytest.fixture
def user_only():
    """Set user credentials for test."""
    config.CURRENT_UI_USERNAME = config.USER_NAME
    config.CURRENT_UI_PASSWORD = config.USER_PASSWD
    config.CURRENT_UI_PROJECT_NAME = config.USER_PROJECT
