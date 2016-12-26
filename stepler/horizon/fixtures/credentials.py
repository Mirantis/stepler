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

__all__ = [
    'admin_only',
    'any_one',
    'user_only'
]


@pytest.fixture(params=('admin', 'user'), scope="session")
def any_one(request,
            credentials,
            admin_project_resources,
            user_project_resources):
    """Session fixture to define user to log in horizon.

    Args:
        request (object): pytest request parametrized with values ``admin``
            and ``user``.

    Note:
        It should be used only in test and never in other fixture in order to
        avoid undefined behavior.

    See also:
        * :func:`admin_only`
        * :func:`user_only`
    """
    resources = {
        'admin': admin_project_resources,
        'user': user_project_resources,
    }[request.param]

    with credentials.change(resources.alias):
        yield


@pytest.fixture
def admin_only(credentials, admin_project_resources):
    """Function fixture to set admin credentials to log in horizon.

    Note:
        It should be used only in test and never in other fixture in order to
        avoid undefined behavior.

    See also:
        * :func:`any_one`
        * :func:`user_only`
    """
    with credentials.change(admin_project_resources.alias):
        yield


@pytest.fixture
def user_only(credentials, user_project_resources):
    """Function fixture to set user credentials to log in horizon.

    Note:
        It should be used only in test and never in other fixture in order to
        avoid undefined behavior.

    See also:
        * :func:`admin_only`
        * :func:`any_one`
    """
    with credentials.change(user_project_resources.alias):
        yield
