"""
-------------
Nova fixtures
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

from novaclient.client import Client
import pytest

from stepler import config

__all__ = [
    'get_nova_client',
    'nova_client',
    'disable_nova_config_drive',
]


@pytest.fixture(scope='session')
def get_nova_client(get_session):
    """Callable session fixture to get nova client.

    Args:
        get_session (keystoneauth1.session.Session): authenticated keystone
            session

    Returns:
        function: function to get nova client
    """
    def _get_nova_client():
        return Client(version=2, session=get_session())

    return _get_nova_client


@pytest.fixture
def nova_client(get_nova_client):
    """Function fixture to get nova client.

    Args:
        get_nova_client (function): function to get nova client

    Returns:
        novaclient.client.Client: authenticated nova client
    """
    return get_nova_client()


@pytest.yield_fixture(scope='module')
def disable_nova_config_drive(os_faults_steps, get_availability_zone_steps):
    """Module fixture to disable nova config drive.

    Note:
        Workaround for bug https://bugs.launchpad.net/mos/+bug/1589460/
        This should be removed in MOS 10.0

    Args:
        os_faults_steps (obj): os-faults steps
        get_availability_zone_steps (function): callable fixture to get
            availability zone steps
    """
    nodes = os_faults_steps.get_nodes(
        service_names=[config.NOVA_API, config.NOVA_COMPUTE])

    with os_faults_steps.patch_ini(
            nodes,
            path=config.NOVA_CONFIG_PATH,
            option='force_config_drive',
            value=False):
        os_faults_steps.restart_service(config.NOVA_API)
        os_faults_steps.restart_service(config.NOVA_COMPUTE)
        zone_steps = get_availability_zone_steps()
        zone_steps.check_all_active_hosts_available()

        yield

    os_faults_steps.restart_service(config.NOVA_API)
    os_faults_steps.restart_service(config.NOVA_COMPUTE)
    zone_steps = get_availability_zone_steps()
    zone_steps.check_all_active_hosts_available()
