"""
---------------
Client fixtures
---------------
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

from ironicclient import client as client_v1
import pytest

from stepler.baremetal import api_clients

__all__ = [
    'api_ironic_client_v1',
    'get_ironic_client',
    'ironic_client_v1',
]


@pytest.fixture(scope='session')
def get_ironic_client(get_session):
    """Callable session fixture to get ironic client v1.

    Args:
        get_session (function): function to get keystone session

    Returns:
        function: function to get ironic client v1
    """
    def _get_ironic_client(version, is_api):
        if version == '1':
            if is_api:
                return api_clients.NodeApiClientV1('1', session=get_session())
            else:
                return client_v1.get_client('1', session=get_session())

        raise ValueError("Unexpected ironic version: {!r}".format(version))

    return _get_ironic_client


@pytest.fixture
def ironic_client_v1(get_ironic_client):
    """Function fixture to get ironic client v1.

    Args:
        get_ironic_client (function): function to get ironic client

    Returns:
        ironicclient.get_client: instantiated ironic client
    """
    return get_ironic_client(version='1', is_api=False)


@pytest.fixture
def api_ironic_client_v1(get_ironic_client):
    """Function fixture to get API ironic client v1.

    Args:
        get_ironic_client (function): function to get ironic client

    Returns:
        api_clients.ApiClientV1: instantiated API ironic client v1
    """
    return get_ironic_client(version='1', is_api=True)
