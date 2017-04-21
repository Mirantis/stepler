"""
---------------
Cinder fixtures
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

from cinderclient import client as cinderclient
import pytest

from stepler.cinder import api_clients
from stepler import config

__all__ = [
    'cinder_client',
    'get_cinder_client',
]


@pytest.fixture(scope='session')
def get_cinder_client(get_session):
    """Callable session fixture to get cinder client.

    Args:
        session (object): authenticated keystone session

    Returns:
        cinderclient.client.Client: instantiated cinder client
    """
    def _get_cinder_client(version, is_api, **credentials):
        api_client = {
            '2': api_clients.ApiClientV2
        }[version]

        session = get_session(**credentials)

        if config.FORCE_API or is_api:
            return api_client(session)
        else:
            return cinderclient.Client(version=version, session=session,
                                       retries=0)

    return _get_cinder_client


@pytest.fixture
def cinder_client(get_cinder_client):
    """Function fixture to get cinder client.

    Args:
        get_cinder_client (function): function to get cinder client

    Returns:
        cinderclient.client.Client: instantiated cinder client
    """
    return get_cinder_client(config.CURRENT_CINDER_VERSION, is_api=False)
