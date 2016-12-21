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
import pytest

__all__ = [
    'get_session',
    'session',
    'uncleanable',
]


@pytest.fixture(scope='session')
def get_session(resource_manager):
    """Callable session fixture to get keystone session.

    Args:
        resource_manager (obj): ProjectResources instance which can
            create keystone session object for current project

    Returns:
        function: function to get session.
    """

    def _get_session(**credentials):
        return resource_manager.get_session(**credentials)

    return _get_session


@pytest.fixture
def session(get_session):
    """Function fixture to get keystone session with default options.

    Args:
        get_session (function): Function to get keystone session.

    Returns:
        Session: Keystone session.

    See also:
        :func:`get_session`
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
    data.nodes_ids = set()
    data.chassis_ids = set()
    data.snapshot_ids = set()
    data.transfer_ids = set()
    data.volume_ids = set()
    return data
