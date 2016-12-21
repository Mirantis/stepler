"""
------------------------
Heat CLI client fixtures
------------------------
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

from stepler.cli_clients import steps

__all__ = [
    'cli_heat_steps',
    'empty_heat_template_path',
]


@pytest.fixture
def cli_heat_steps(remote_executor, os_credentials):
    """Function fixture to get heat CLI steps.

    Args:
        remote_executor (callable): function to execute command on remote node

    Returns:
        object: initialized heat CLI steps
    """
    return steps.CliHeatSteps(remote_executor, os_credentials.openrc_path)


@pytest.yield_fixture
def empty_heat_template_path(nova_api_node,
                             get_template_path,
                             os_faults_steps):
    """Upload empty heat template to `nova_api_node` and return its path.

    Delete uploaded file on teardown.

    Args:
        nova_api_node (obj): controller (node with nova-api service)
        get_template_path (callable): function to get local path to template
        os_faults_steps (obj): initialized os-faults steps

    Returns:
        str: path to template on `nova_api_node`
    """
    template_path = get_template_path('empty_heat_template')
    remote_path = os_faults_steps.upload_file(nova_api_node, template_path)
    yield remote_path
    os_faults_steps.execute_cmd(nova_api_node, 'rm {}'.format(remote_path))
