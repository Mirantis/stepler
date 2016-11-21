"""
---------------
Agents fixtures
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

from stepler.neutron import steps

__all__ = [
    'get_agent_steps',
    'agent_steps',
]


@pytest.fixture(scope="session")
def get_agent_steps(get_neutron_client):
    """Callable session fixture to get agent steps.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client

    Returns:
        function: function to get instantiated agent steps
    """

    def _get_steps(**credentials):
        return steps.AgentSteps(get_neutron_client(**credentials).agents)

    return _get_steps


@pytest.fixture
def agent_steps(get_agent_steps):
    """Function fixture to get agent steps.

    Args:
        get_agent_steps (function): function to get instantiated agent
            steps

    Returns:
        stepler.neutron.steps.AgentSteps: instantiated agent steps
    """
    return get_agent_steps()
