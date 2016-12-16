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
from stepler.third_party import utils

__all__ = ['change_glance_credentials', ]


@pytest.fixture
def change_glance_credentials(os_faults_steps, glance_steps, user_steps):
    """Function fixture to change glance credentials in config and keystone.

    Original credentials will be restored after test.

    Args:
        os_faults_steps (obj): instantiated os-faults steps
        glance_steps (obj): instantiated glance steps
        user_steps (obj): instantiated user-steps
    """

    glance_nodes = os_faults_steps.get_nodes(service_names=[config.GLANCE_API])
    cmd = ("awk '/^password=/{split($1,val,\"=\"); print val[2]}' " +
           config.GLANCE_API_CONFIG_PATH)
    old_password = os_faults_steps.execute_cmd(glance_nodes.pick(),
                                               cmd)[0].payload['stdout']
    glance_user = user_steps.get_user(config.GLANCE_USER)

    new_password, = utils.generate_ids()
    user_steps.update_user(glance_user, password=new_password)
    api_backup_path = os_faults_steps.patch_ini_file(
        glance_nodes,
        config.GLANCE_API_CONFIG_PATH,
        section='keystone_authtoken',
        option='password',
        value=new_password)
    swift_backup_path = os_faults_steps.patch_ini_file(
        glance_nodes,
        config.GLANCE_SWIFT_CONFIG_PATH,
        section='ref1',
        option='key',
        value=new_password)

    os_faults_steps.restart_services([config.GLANCE_API])
    glance_steps.check_glance_service_available()

    yield

    os_faults_steps.restore_backup(
        glance_nodes, config.GLANCE_SWIFT_CONFIG_PATH, swift_backup_path)
    os_faults_steps.restore_backup(glance_nodes, config.GLANCE_API_CONFIG_PATH,
                                   api_backup_path)

    user_steps.update_user(glance_user, password=old_password)
    os_faults_steps.restart_services([config.GLANCE_API])
    glance_steps.check_glance_service_available()
