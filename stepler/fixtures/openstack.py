"""
------------------
Openstack fixtures
------------------
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

import attrdict
from keystoneauth1 import identity
from keystoneauth1 import session as _session
import pytest

from stepler import config

__all__ = [
    'get_session',
    'session',
    'uncleanable',
]


@pytest.fixture(scope='session')
def get_session():
    """Callable session fixture to get session.

    Can be called several times during a test to regenerate keystone session.

    Returns:
        function: function to get session.
    """
    assert config.AUTH_URL, "Environment variable OS_AUTH_URL is not defined"

    def _get_session(auth_url=None,
                     username=None,
                     password=None,
                     project_name=None,
                     user_domain_name=None,
                     project_domain_name=None):
        auth_url = auth_url or config.AUTH_URL
        username = username or config.USERNAME
        password = password or config.PASSWORD
        project_name = project_name or config.PROJECT_NAME
        user_domain_name = user_domain_name or config.USER_DOMAIN_NAME
        project_domain_name = project_domain_name or config.PROJECT_DOMAIN_NAME

        if config.KEYSTONE_API_VERSION == 3:

            auth = identity.v3.Password(
                auth_url=auth_url,
                username=username,
                user_domain_name=user_domain_name,
                password=password,
                project_name=project_name,
                project_domain_name=project_domain_name)

        elif config.KEYSTONE_API_VERSION == 2:

            auth = identity.v2.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                tenant_name=project_name)

        else:
            raise ValueError("Unexpected keystone API version: {}".format(
                config.KEYSTONE_API_VERSION))

        return _session.Session(auth=auth)

    return _get_session


@pytest.fixture
def session(get_session):
    """Function fixture to get session.

    Returns:
      keystoneauth1.session.Session: instantiated keystone session
    """
    return get_session()


@pytest.fixture(scope='session')
def uncleanable():
    """Session fixture to get data structure with resources not to cleanup.

    Each test uses cleanup resources mechanism, but some resources should be
    skipped there, because they should be present during several tests. This
    data structure contains such resources.
    """
    data = attrdict.AttrDict()
    data.backup_ids = set()
    data.image_ids = set()
    data.keypair_ids = set()
    data.server_ids = set()
    data.snapshot_ids = set()
    data.transfer_ids = set()
    data.volume_ids = set()
    return data
