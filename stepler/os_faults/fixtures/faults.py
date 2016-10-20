"""
------------------
os_faults fixtures
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

try:
    import os_faults
except ImportError:
    import warnings
    warnings.warn(
        'os_faults import is skipped for docs generating only', ImportWarning)

import pytest

from stepler import config
from stepler.os_faults.steps import OsFaultsSteps

__all__ = [
    'os_faults_client',
    'os_faults_steps',
    'modify_config_file'
]


@pytest.fixture
def os_faults_client():
    """Fixture to get os_faults client.

     Returns:
         destructor: instantiated os_faults client
     """
    assert config.OS_FAULTS_CONFIG, ("Environment variable OS_FAULTS_CONFIG "
                                     "is not defined")

    destructor = os_faults.connect(config_filename=config.OS_FAULTS_CONFIG)
    destructor.verify()
    return destructor


@pytest.fixture
def os_faults_steps(os_faults_client):
    """Fixture to get os_faults steps.

    Args:
        os_faults_client (object): instantiated os_faults client

    Returns:
        stepler.os_faults.steps.OsFaultsSteps: instantiated os_faults steps
    """
    return OsFaultsSteps(os_faults_client)


@pytest.fixture
def modify_config_file(os_faults_steps):
    """Fixture to modify config files and restart services.

    Can be called several times during test.

    Args:
        os_faults_steps: instantiated os_faults steps.
    """
    nodes_paths = []
    service_names = []

    def _correct_config_file(nodes, path, option, value, section=None,
                             service_name=None):
        os_faults_steps.modify_file(nodes, path, option, value, section)
        nodes_paths.append([nodes, path])
        if service_name:
            os_faults_steps.restart_service(service_name)
            service_names.append(service_name)

    yield _correct_config_file

    for nodes, path in nodes_paths:
        os_faults_steps.restore_backup(nodes, path)

    for service_name in service_names:
        os_faults_steps.restart_service(service_name)
