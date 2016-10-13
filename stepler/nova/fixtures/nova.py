"""
-------------
Nova fixtures
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

from novaclient.client import Client
import pytest

__all__ = [
    'get_nova_client',
    'nova_client',
]


@pytest.fixture(scope='session')
def get_nova_client(get_session):
    """Callable session fixture to get nova client.

    Args:
        get_session (keystoneauth1.session.Session): authenticated keystone
            session

    Returns:
        function: function to get nova client
    """
    def _get_nova_client():
        return Client(version=2, session=get_session())


@pytest.fixture
def nova_client(get_nova_client):
    """Function fixture to get nova client.

    Args:
        get_nova_client (function): function to get nova client

    Returns:
        novaclient.client.Client: authenticated nova client
    """
    return get_nova_client()
