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

from ironicclient import client as Client
import pytest

from stepler import config

__all__ = [
    'ironic_client'
]


@pytest.fixture
def ironic_client(session):
    """Fixture to get ironic client."""

    session = {
        'os_username': config.USERNAME,
        'os_password': config.PASSWORD,
        'os_auth_url': config.AUTH_URL[:-2],
        'os_tenant_name': config.PROJECT_NAME
    }

    return Client.get_client('1', **session)
