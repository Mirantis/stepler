"""
---------------
Ironic fixtures
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

from ironicclient import client
import pytest

from stepler import config

__all__ = [
    'get_ironic_client',
    'ironic_client'
]


@pytest.fixture(scope="session")
def get_ironic_client(get_session):
    """Callable session fixture to get ironic client.

    Args:
        get_session (function): function to get authenticated ironic session

    Returns:
        function: function to get ironic client
    """
    def _get_client(**credentials):
        return client.get_client(config.CURRENT_IRONIC_VERSION,
                                 session=get_session(**credentials))
    return _get_client


@pytest.fixture
def ironic_client(get_ironic_client):
    """Callable function fixture to get ironic client.

    Args:
        get_ironic_client (function): function to get keystone session

    Returns:
        ironicclient.v1.client.: instantiated ironic client
    """
    return get_ironic_client()
