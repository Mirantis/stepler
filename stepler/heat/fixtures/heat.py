"""
-------------
Heat fixtures
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

from heatclient import client as heatclient
import pytest


__all__ = [
    'heat_client',
]


@pytest.fixture
def heat_client(session):
    """Function fixture to get heat client.

    Args:
        session (object): authenticated keystone session

    Returns:
        heatclient.Client: instantiated heat client
    """
    token = session.get_token()
    endpoint_url = session.get_endpoint(
        service_type='orchestration',
        endpoint_type='publicURL'
    )
    return heatclient.Client(version=1, endpoint=endpoint_url, token=token)
