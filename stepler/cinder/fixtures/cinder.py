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

from stepler import config

__all__ = [
    'cinder_client',
    'get_cinder_client',
]


@pytest.fixture()
def get_cinder_client(get_session):
    """Callable session fixture to get nova client.

    Args:
        get_session (keystoneauth1.session.Session): authenticated keystone
            session

    Returns:
        function: function to get nova client
    """
    def _get_cinder_client(*args, **kwargs):
        return cinderclient.Client(version=config.CURRENT_CINDER_VERSION,
                                   session=get_session(*args, **kwargs))

    return _get_cinder_client


@pytest.fixture
def cinder_client(get_cinder_client):
    """Function fixture to get cinder client.

    Args:
        session (object): authenticated keystone session

    Returns:
        cinderclient.client.Client: instantiated cinder client
    """
    return get_cinder_client()
