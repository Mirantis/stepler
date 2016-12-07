"""
---------------------
Neutron agent manager
---------------------
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

from stepler.neutron.client import base


class Agent(base.Resource):
    pass


class AgentManager(base.BaseNeutronManager):
    """Agent (neutron) manager."""

    NAME = 'agent'
    _resource_class = Agent

    @base.transform_many
    def get_dhcp_agents_for_network(self, network_id):
        """Get network DHCP agents list.

        Args:
            network_id (str): network id to get DHCP agents

        Returns:
            list: list of dicts of DHCP agents
        """
        dhcp_agents = self._rest_client.list_dhcp_agent_hosting_networks(
            network_id)
        return dhcp_agents['agents']

    @base.transform_many
    def get_l3_agents_for_router(self, router_id):
        """Get router L3 agents list.

        Args:
            router_id (str): router id to get L3 agents

        Returns:
            list: list of dicts of L3 agents
        """
        l3_agents = self._rest_client.list_l3_agent_hosting_routers(router_id)
        return l3_agents['agents']

    def remove_network_from_dhcp_agent(self, dhcp_agent_id, network_id):
        """Remove network from DHCP agent.

        Args:
            dhcp_agent_id (str): DHCP agent id to remove network from
            network_id (str): network id to remove from DHCP agent
        """
        self._rest_client.remove_network_from_dhcp_agent(dhcp_agent_id,
                                                         network_id)

    def add_network_to_dhcp_agent(self, dhcp_agent_id, network_id):
        """Add network to DHCP agent.

        Args:
            dhcp_agent_id (str): DHCP agent id to add network to
            network_id (str): network id to add to DHCP agent
        """
        self._rest_client.add_network_to_dhcp_agent(dhcp_agent_id,
                                                    {'network_id': network_id})

    def remove_router_from_l3_agent(self, l3_agent_id, router_id):
        """Remove router from L3 agent.

        Args:
            l3_agent_id (str): L3 agent id to remove router from
            router_id (str): router id to remove from L3 agent
        """
        self._rest_client.remove_router_from_l3_agent(l3_agent_id,
                                                      router_id)

    def add_router_to_l3_agent(self, l3_agent_id, router_id):
        """Add router to L3 agent.

        Args:
            l3_agent_id (str): L3 agent id to add router to
            router_id (str): router id to add to L3 agent
        """
        self._rest_client.add_router_to_l3_agent(l3_agent_id,
                                                 {'router_id': router_id})
