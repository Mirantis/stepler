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

from keystoneauth1 import exceptions as keystone_exceptions
from novaclient.api_versions import APIVersion
from novaclient.client import Client
from novaclient import exceptions as nova_exceptions
import pytest

from stepler import config
from stepler.third_party import waiter

__all__ = [
    'get_nova_client',
    'nova_client',
    'disable_nova_config_drive',
    'skip_live_migration_tests',
    'unlimited_live_migrations',
    'nova_ceph_enabled',
    'disable_nova_use_cow_images',
    'big_nova_reclaim_instance_interval',
    'small_nova_reclaim_instance_interval',
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

    def _wait_client_availability(**credentials):
        client = Client(
            version=config.CURRENT_NOVA_VERSION,
            session=get_session(**credentials))

        current_microversion = client.versions.find(status='CURRENT').version
        client.api_version = APIVersion(current_microversion)

        return client

    def _get_nova_client(**credentials):
        return waiter.wait(
            _wait_client_availability,
            kwargs=credentials,
            timeout_seconds=config.NOVA_AVAILABILITY_TIMEOUT,
            expected_exceptions=(keystone_exceptions.ClientException,
                                 nova_exceptions.ClientException))

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


def change_nova_config(option, value, scope='function', services=None):
    """Fixtures to change nova config and restart nova factory.

    Args:
        option (str): option to change
        value (str|int): desired value
        scope (str, optional): returned fixture scope. `function` by default
        services (list, optional): list of services to restart. By default is
            [config.NOVA_API, config.NOVA_COMPUTE]

    Returns:
        function: fixture
    """
    services = services or [config.NOVA_API, config.NOVA_COMPUTE]

    @pytest.fixture(scope=scope)
    def _change_nova_config(patch_ini_file_and_restart_services,
                            get_availability_zone_steps):
        with patch_ini_file_and_restart_services(
                services,
                file_path=config.NOVA_CONFIG_PATH,
                option=option,
                value=value):
            zone_steps = get_availability_zone_steps()
            zone_steps.check_all_active_hosts_available()

            yield

        zone_steps = get_availability_zone_steps()
        zone_steps.check_all_active_hosts_available()

    return _change_nova_config


# Workaround for bug https://bugs.launchpad.net/mos/+bug/1589460/
# This should be removed in MOS 10.0
disable_nova_config_drive = change_nova_config(
    'force_config_drive', False, scope='module')

disable_nova_use_cow_images = change_nova_config(
    'use_cow_images', 0, services=[config.NOVA_COMPUTE])

big_nova_reclaim_instance_interval = change_nova_config(
    'reclaim_instance_interval', config.BIG_RECLAIM_INTERVAL)
small_nova_reclaim_instance_interval = change_nova_config(
    'reclaim_instance_interval', config.SMALL_RECLAIM_INTERVAL)

unlimited_live_migrations = change_nova_config(
    'max_concurrent_live_migrations', 0, scope='module')


@pytest.fixture
def nova_ceph_enabled(os_faults_steps):
    """Function fixture to retrieve is Ceph is used by Nova.

    Args:
        os_faults_steps (obj): instantiated os-faults steps

    Returns:
        bool: is Ceph used by Nova or not
    """
    cmd = "grep -P '^images_type\s*=\s*rbd' {}".format(config.NOVA_CONFIG_PATH)
    computes = os_faults_steps.get_compute_nodes()
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
