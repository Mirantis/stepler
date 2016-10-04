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

import os_faults
import pytest

from stepler import config
from stepler.os_faults.steps import OsFaultsSteps

__all__ = [
    'os_faults_client',
    'os_faults_steps'
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
