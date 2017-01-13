"""
----------------
Service fixtures
----------------
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

from stepler.keystone import steps

__all__ = [
    'get_service_steps',
    'service_steps'
]


@pytest.fixture(scope="session")
def get_service_steps(get_keystone_client):
    """Callable session fixture to get service steps.

    Args:
        get_keystone_client (function): function to get keystone client

    Returns:
        function: function to get project steps
    """
    def _get_steps(**credentials):
        return steps.ServiceSteps(get_keystone_client(**credentials).services)

    return _get_steps


@pytest.fixture
def service_steps(get_service_steps):
    """Function fixture to get service steps.

    Args:
        get_service_steps (function): function to get service steps

    Returns:
        ServiceSteps: instantiated service steps
    """
    return get_service_steps()
