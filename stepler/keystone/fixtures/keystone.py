"""
-----------------
Keystone fixtures
-----------------
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

from keystoneclient import client

__all__ = [
    'get_keystone_client',
    'keystone_client',
]


@pytest.fixture(scope="session")
def get_keystone_client(get_session):
    """Callable session fixture to get keystone client.

    Args:
        get_session (function): function to get authenticated keystone
            session

    Returns:
        function: function to get keystone client
    """
    def _get_client(**credentials):
        return client.Client(session=get_session(**credentials))
    return _get_client


@pytest.fixture
def keystone_client(get_keystone_client):
    """Function fixture to get keystone client.

    Args:
        get_keystone_client (function): function to get keystone client

    Returns:
        keystoneclient.client.Client: authenticated keystone client
    """
    return get_keystone_client()
