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
    'skip_live_migration_tests',
    'unlimited_live_migrations',
    'nova_ceph_enabled',
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
def disable_nova_config_drive(patch_ini_file_and_restart_services,
                              get_availability_zone_steps):
    """Module fixture to disable nova config drive.

    Note:
        Workaround for bug https://bugs.launchpad.net/mos/+bug/1589460/
        This should be removed in MOS 10.0

    Args:
        patch_ini_file_and_restart_services (function): callable fixture to
            patch ini file and restart services
        get_availability_zone_steps (function): callable fixture to get
            availability zone steps
    """
    with patch_ini_file_and_restart_services(
            [config.NOVA_API, config.NOVA_COMPUTE],
            file_path=config.NOVA_CONFIG_PATH,
            option='force_config_drive',
            value=False):
        zone_steps = get_availability_zone_steps()
        zone_steps.check_all_active_hosts_available()

        yield

    zone_steps = get_availability_zone_steps()
    zone_steps.check_all_active_hosts_available()


@pytest.yield_fixture(scope='module')
def unlimited_live_migrations(patch_ini_file_and_restart_services,
                              get_availability_zone_steps):
    """Module fixture to allow unlimited live migration.

    Args:
        patch_ini_file_and_restart_services (function): callable fixture to
            patch ini file and restart services
        get_availability_zone_steps (function): callable fixture to get
            availability zone steps
    """
    with patch_ini_file_and_restart_services(
            [config.NOVA_API, config.NOVA_COMPUTE],
            file_path=config.NOVA_CONFIG_PATH,
            option='max_concurrent_live_migrations',
            value=0):
        zone_steps = get_availability_zone_steps()
        zone_steps.check_all_active_hosts_available()

        yield

    zone_steps = get_availability_zone_steps()
    zone_steps.check_all_active_hosts_available()


@pytest.fixture
def nova_ceph_enabled(os_faults_steps):
    """Function fixture to retrieve is Ceph is used by Nova.

    Args:
        os_faults_steps (obj): instantiated os-faults steps

    Returns:
        bool: is Ceph used by Nova or not
    """
    cmd = "grep -P '^images_type\s*=\s*rbd' {}".format(config.NOVA_CONFIG_PATH)
    computes = os_faults_steps.get_nodes(service_names=[config.NOVA_COMPUTE])
    result = os_faults_steps.execute_cmd(computes, cmd, check=False)
    return all(node_result.status == config.STATUS_OK
               for node_result in result)


@pytest.fixture
def skip_live_migration_tests(request, nova_ceph_enabled):
    """Skip tests with wrong `block_migration` parameter.

    Block migration requires Nova Ceph RBD to be disabled. This fixture skips
    parametrized with `block_migration` tests with wrong `block_migration`
    value (not suitable for current cloud).

    Args:
        request (obj): py.test SubRequest instance
        nova_ceph_enabled (bool): is Ceph used by Nova or not
    """
    if not hasattr(request.node, 'callspec'):
        return
    block_migration = request.node.callspec.params.get('block_migration')
    if block_migration is None:
        return
    if block_migration and nova_ceph_enabled:
        pytest.skip("Block migration requires Nova Ceph RBD to be disabled")
