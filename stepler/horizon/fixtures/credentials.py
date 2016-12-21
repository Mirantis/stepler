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

import os

import pytest

from stepler import config

__all__ = [
    'admin_only',
    'any_one',
    'user_only'
]


@pytest.fixture(params=('admin', 'user'), scope="session")
def any_one(request,
            credentials,
            test_env,
            user_project_resources):
    """Define user to log in account."""

    if request.param == 'admin':
        # TODO(agromov): replace 'os.environ' usage with 'credentials' fixture
        os.environ['OS_LOGIN'] = config.ADMIN_NAME
        os.environ['OS_PASSWD'] = config.ADMIN_PASSWD
        os.environ['OS_PROJECT'] = config.ADMIN_PROJECT
        yield

    if request.param == 'user':
        os.environ['OS_LOGIN'] = config.USER_NAME
        os.environ['OS_PASSWD'] = config.USER_PASSWD
        os.environ['OS_PROJECT'] = config.USER_PROJECT

        creds_alias = user_project_resources.alias
        with credentials.change(creds_alias):
            yield


@pytest.fixture
def admin_only(test_env):
    """Set admin credentials for test."""
    os.environ['OS_LOGIN'] = config.ADMIN_NAME
    os.environ['OS_PASSWD'] = config.ADMIN_PASSWD
    os.environ['OS_PROJECT'] = config.ADMIN_PROJECT


@pytest.fixture
def user_only(credentials,
              test_env,
              user_project_resources):
    """Set user credentials for test."""
    os.environ['OS_LOGIN'] = config.USER_NAME
    os.environ['OS_PASSWD'] = config.USER_PASSWD
    os.environ['OS_PROJECT'] = config.USER_PROJECT

    creds_alias = user_project_resources.alias
    with credentials.change(creds_alias):
        yield
