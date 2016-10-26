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

import functools

import pytest

__all__ = [
    'remote_executor',
]


@pytest.fixture
def remote_executor(nova_api_node, os_faults_steps):
    """Function fixture to get remote command executor.

    Args:
        nova_api_node (obj): controller (node with nova-api service)
        os_faults_steps (obj): initialized os-faults steps

    Returns:
        callable: function to execute command on `nova_api_node`
    """
    return functools.partial(os_faults_steps.execute_cmd, nodes=nova_api_node)
