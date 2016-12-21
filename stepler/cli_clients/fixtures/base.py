"""
-----------------
Base CLI fixtures
-----------------
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
    'remote_executor',
]


@pytest.fixture
def remote_executor(nova_api_node, os_faults_steps, os_credentials):
    """Function fixture to get remote command executor.

    Args:
        nova_api_node (obj): controller (node with nova-api service)
        os_faults_steps (object): instantiated os_faults steps
        os_credentials (AttrDict): data structure with credentials to be used

    Returns:
        callable: function to execute command on `nova_api_node`
    """
    def _execute_cli(cmd, use_openrc=True, environ=None, **kwargs):
        environ = environ or {}

        if use_openrc:
            source_cmd = config.OPENRC_ACTIVATE_CMD + ";"

            environ['OS_PROJECT_NAME'] = os_credentials.project_name
            environ['OS_TENANT_NAME'] = os_credentials.project_name
            environ['OS_USERNAME'] = os_credentials.username
            environ['OS_PASSWORD'] = os_credentials.password
        else:
            source_cmd = ""

        environ_string = ' '.join("{0}='{1}'".format(*item)
                                  for item in environ.items())

        cmd = u"{source_cmd} {env} {command}".format(source_cmd=source_cmd,
                                                     env=environ_string,
                                                     command=cmd)

        return os_faults_steps.execute_cmd(nodes=nova_api_node, cmd=cmd,
                                           **kwargs)

    return _execute_cli
