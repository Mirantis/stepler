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

__all__ = [
    'ironic_client'
]


@pytest.fixture
def ironic_client(session):
    """Fixture to get ironic client."""
    # import pdb; pdb.set_trace()

    session = {'os_username': 'admin',
              'os_password': 'admin',
              'os_auth_url': 'http://192.168.0.2:5000/',
              'os_tenant_name': 'admin'}

    return Client.get_client('1', **session)
