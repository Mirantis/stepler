"""
Openstack fixtures.

@author: schipiga@mirantis.com
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

from keystoneauth1.identity import v3
from keystoneauth1 import session as _session
import pytest

from stepler import config

__all__ = [
    'session'
]


@pytest.fixture
def session():
    """Fixture to get session."""
    auth = v3.Password(auth_url=config.AUTH_URL,
                       username=config.USERNAME,
                       user_domain_name=config.USER_DOMAIN_NAME,
                       password=config.PASSWORD,
                       project_name=config.PROJECT_NAME,
                       project_domain_name=config.PROJECT_DOMAIN_NAME)
    return _session.Session(auth=auth)
