"""
------------------------
Neutron DHCP agent tests
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

import signal

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
    #. Check DHCP on cirros-dhcpc command on server with sudo
    #. Get node with DHCP agent for network
    #. Ban DHCP agent for the node with pcs
    #. Wait for DHCP agent becoming dead
    #. Check that killed dhcp-agent does not in dhcp-agents list
        for network
    #. Repeat last 4 steps if ban_count is 2
    #. Check that this network is on another health dhcp-agent
    #. Check DHCP on cirros-dhcpc command on server with sudo

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


@pytest.mark.requires("dhcp_agent_nodes_count >= 2")
@pytest.mark.idempotent_id('5fea925f-e7a2-4524-80c2-c4f632c304c9')
def test_dhcp_agent_after_drop_rabbit_port(network,
                                           nova_floating_ip,
                                           server,
                                           server_steps,
                                           os_faults_steps,
                                           agent_steps):
    """**Scenario:** Drop rabbit port and check dhcp-agent work.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Check DHCP on cirros-dhcpc command on server with sudo
    #. Get node with DHCP agent for network
    #. Drop rabbit's port 5673 using iptables for node from the previous step
    #. Wait for DHCP agent becoming dead
    #. Check that dhcp-agent does not in dhcp-agents list for network
    #. Check that network is on 2 health DHCP-agents
    #. Check DHCP on cirros-dhcpc command on server with sudo
    #. Remove rule for dropping port using iptables
    #. Check that all neutron agents are alive

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

    all_dhcp_agents = agent_steps.get_agents(
        binary=config.NEUTRON_DHCP_SERVICE)

    dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
    nodes_with_dhcp = os_faults_steps.get_nodes_for_agents([dhcp_agent])
    os_faults_steps.add_rule_to_drop_port(nodes_with_dhcp, config.RABBIT_PORT)
    agent_steps.check_alive([dhcp_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    agent_steps.check_network_rescheduled(
        network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    agent_steps.check_agents_count_for_net(network, expected_count=2)
    server_steps.check_dhcp_on_cirros_server(server)

    os_faults_steps.remove_rule_to_drop_port(nodes_with_dhcp,
                                             config.RABBIT_PORT)
    agent_steps.check_alive(all_dhcp_agents,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('09a8280b-38b2-4414-bc88-665a3843ee6c')
def test_ban_dhcp_agent_many_times(network,
                                   nova_floating_ip,
                                   server,
                                   server_steps,
                                   os_faults_steps,
                                   agent_steps):
    """**Scenario:** Ban dhcp-agent many times.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Check DHCP on cirros-dhcpc command on server with sudo
    #. Get nodes with DHCP agents not hosting network
    #. Ban all DHCP agents not hosting network
    #. Wait for banned DHCP agents becoming dead
    #. Get node with DHCP agent for network
    #. Ban DHCP agent for network with pcs
    #. Clear DHCP agent for network with pcs
    #. Repeat last 2 steps 40 times
    #. Check that neutron agent from the previous step is alive
    #. Check that network is on 2 health DHCP-agents
    #. Check DHCP on cirros-dhcpc command on server with sudo

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

    agent_to_ban = agent_steps.get_dhcp_agents_for_net(network)[0]
    free_agents = agent_steps.get_dhcp_agents_not_hosting_net(network)

    nodes_with_free_agents = os_faults_steps.get_nodes_for_agents(free_agents)
    os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=nodes_with_free_agents)
    agent_steps.check_alive(free_agents,
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    node_with_dhcp = os_faults_steps.get_nodes_for_agents([agent_to_ban])
    for _ in range(40):
        os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                          nodes=node_with_dhcp)
        os_faults_steps.start_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=node_with_dhcp)

    agent_steps.check_alive([agent_to_ban],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    agent_steps.check_agents_count_for_net(network, expected_count=2)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.idempotent_id('a771c0e1-58c0-4b44-8fe2-a3d557504751')
@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
def test_kill_check_dhcp_agents(network,
                                nova_floating_ip,
                                server,
                                server_steps,
                                os_faults_steps,
                                agent_steps):
    """**Scenario:** Kill process and check dhcp-agents.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Check DHCP on cirros-dhcpc command on server with sudo
    #. Get node with DHCP agent for network
    #. Kill dhcp-agent process
    #. Wait and check that dhcp agent has status active
    #. Check that network is on the health dhcp-agents
    #. Check DHCP on cirros-dhcpc command on server with sudo

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
    dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
    nodes_with_dhcp = os_faults_steps.get_nodes_for_agents([dhcp_agent])
    pid = os_faults_steps.get_process_pid(nodes_with_dhcp,
                                          config.NEUTRON_DHCP_SERVICE)
    os_faults_steps.send_signal_to_process(nodes_with_dhcp,
                                           pid=pid,
                                           signal=signal.SIGKILL)
    agent_steps.check_alive([dhcp_agent],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    agent_steps.check_agents_count_for_net(network, expected_count=2)
    dhcp_agents = agent_steps.get_dhcp_agents_for_net(network)
    agent_steps.check_alive(dhcp_agents,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    server_steps.check_dhcp_on_cirros_server(server)
