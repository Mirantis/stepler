"""
------------------------
Neutron dhcp agent tests
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

from stepler import config


pytestmark = [pytest.mark.requires("computes_count >= 2"),
              pytest.mark.destructive]


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('7936df3e-2d28-4534-8d72-679749afd83d',
                           ban_count=1)
@pytest.mark.idempotent_id('aaf8a643-99ad-4e8e-bd03-934e99e3e150',
                           ban_count=2)
@pytest.mark.parametrize('ban_count', [1, 2])
def test_ban_some_dhcp_agents(network,
                              nova_floating_ip,
                              server,
                              server_steps,
                              os_faults_steps,
                              agent_steps,
                              ban_count):
    """**Scenario:** Ban dhcp-agent and check cirros-dhcpc command on server.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Check dhcp on cirros-dhcpc command on server with sudo
    #. Get node with dhcp agent for network
    #. Ban dhcp agent for the node with pcs
    #. Wait for dhcp agent becoming dead
    #. Check that killed dhcp-agent does not in dhcp-agents list
        for network
    #. Repeat last 4 steps if ban_count is 2
    #. Check that this network is on another health dhcp-agent
    #. Check dhcp on cirros-dhcpc command on server with sudo

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)

    for _ in range(ban_count):
        dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
        nodes_with_dhcp = os_faults_steps.get_nodes_for_agents([dhcp_agent])
        os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                          nodes=nodes_with_dhcp)
        agent_steps.check_alive([dhcp_agent],
                                must_alive=False,
                                timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
        agent_steps.check_network_rescheduled(
            network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    agent_steps.get_dhcp_agents_for_net(network)
    server_steps.check_dhcp_on_cirros_server(server)
