"""
----------------
Horizon conftest
----------------

Contains fixtures specific for horizon (UI testing).

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

import os
import shutil

import pytest

from . import config
from .fixtures import *  # noqa
from .utils import slugify

__all__ = [
    'access_steps',
    'create_security_group',
    'security_group',

    'api_access_steps',

    'auth_steps',
    'horizon',
    'login',

    'logger',
    'report_dir',
    'video_capture',
    'virtual_display',
    'test_env',

    'create_container',
    'container',
    'containers_steps',

    'admin_only',
    'any_one',
    'user_only',

    'defaults_steps',
    'update_defaults',

    'create_flavor',
    'create_flavors',
    'flavor',
    'flavors_steps',

    'allocate_floating_ip',
    'floating_ip',
    'floating_ips_steps',

    'create_host_aggregate',
    'create_host_aggregates',
    'host_aggregate',
    'host_aggregates_steps',

    'create_image',
    'create_images',
    'image',
    'images_steps',

    'create_instance',
    'instance',
    'instances_steps',

    'import_keypair',
    'keypair',
    'keypairs_steps',

    'create_namespace',
    'namespace',
    'namespaces_steps',

    'create_network',
    'create_networks',
    'network',
    'networks_steps',

    'create_project',
    'project',
    'projects_steps',

    'create_router',
    'router',
    'routers_steps',

    'settings_steps',
    'update_settings',

    'create_user',
    'create_users',
    'user',
    'users_steps',

    'qos_spec',
    'volume_type',
    'volume_types_steps',

    'create_backups',
    'create_snapshot',
    'create_snapshots',
    'create_volume',
    'create_volumes',
    'snapshot',
    'volume',
    'volumes_steps',
]

__all__.sort()


def pytest_configure(config):
    """Pytest configure hook."""
    if not hasattr(config, 'slaveinput'):
        # on xdist-master node do all the important stuff
        if os.path.exists(config.TEST_REPORTS_DIR):
            shutil.rmtree(config.TEST_REPORTS_DIR)
        os.mkdir(config.TEST_REPORTS_DIR)
        if os.path.exists(config.XVFB_LOCK):
            os.remove(config.XVFB_LOCK)


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """Pytest hook to delete test report if it is passed."""
    if not hasattr(item, 'is_passed'):
        item.is_passed = True

    outcome = yield
    rep = outcome.get_result()

    if not rep.passed:
        item.is_passed = False

    if rep.when == 'teardown' and item.is_passed:
        shutil.rmtree(os.path.join(config.TEST_REPORTS_DIR,
                                   slugify(item.name)))
