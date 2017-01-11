"""
--------------------------------
Neutron basic verification tests
--------------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest


@pytest.mark.idempotent_id('5a3a0b95-20c7-403a-9b2b-4d26fc10669a')
def test_networks_list(network_steps):
    """**Scenario:** Request list of networks.

    **Steps:**

    #. Get list of networks
    """
    network_steps.get_networks()


@pytest.mark.idempotent_id('e05e3a60-14ff-4a12-8d09-0762f5ceffa1')
def test_agents_list(agent_steps):
    """**Scenario:** Request list of neutron agents.

    **Steps:**

    #. Get list of neutron agents
    #. Check that all agents are up and running
    """
    agents = agent_steps.get_agents()
    agent_steps.check_alive(agents)
