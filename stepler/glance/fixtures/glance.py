"""
---------------
Glance fixtures
---------------
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

import pytest

from stepler import config

__all__ = [
    'set_glance_storage_to_file_with_quota',
    'enable_multi_locations',
]


@pytest.fixture(scope='module')
def set_glance_storage_to_file_with_quota(os_faults_steps, get_glance_steps):
    """Fixture to set glance storage to file and set user_storage_quota.

    Args:
        os_faults_steps (obj): instantiated os-faults steps
        get_glance_steps (function): function to get glance steps.
    """
    first_backup = None
    new_params = (
        ('glance_store', 'stores', 'file,http'),
        ('glance_store', 'default_store', 'file'),
        (None, 'user_storage_quota', config.GLANCE_USER_STORAGE_QUOTA), )
    nodes = os_faults_steps.get_nodes(service_names=config.GLANCE_SERVICES)
    for section, option, value in new_params:
        backup = os_faults_steps.patch_ini_file(
            nodes,
            config.GLANCE_CONFIG_PATH,
            option=option,
            value=value,
            section=section)
        first_backup = first_backup or backup
    os_faults_steps.restart_services(config.GLANCE_SERVICES)
    glance_steps = get_glance_steps(
        version=config.CURRENT_GLANCE_VERSION, is_api=False)
    glance_steps.check_glance_service_available()

    yield

    os_faults_steps.restore_backup(nodes, config.GLANCE_CONFIG_PATH,
                                   first_backup)
    os_faults_steps.restart_services(config.GLANCE_SERVICES)
    glance_steps.check_glance_service_available()


@pytest.fixture
def enable_multi_locations(patch_ini_file_and_restart_services,
                           get_glance_steps):
    """Fixture to enable glance multiple locations.

    Args:
        patch_ini_file_and_restart_services (function): callable fixture to
            patch ini file and restart services
        get_glance_steps (function): callable session fixture to get
            glance steps.
    """
    with patch_ini_file_and_restart_services(
        [config.GLANCE_API],
            file_path=config.GLANCE_API_CONFIG_PATH,
            option='show_multiple_locations',
            value=True):
        glance_steps = get_glance_steps(
            version=config.CURRENT_GLANCE_VERSION, is_api=False)
        glance_steps.check_glance_service_available()

        yield

    glance_steps.check_glance_service_available()
