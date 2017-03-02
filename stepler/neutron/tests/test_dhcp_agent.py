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
                              floating_ip,
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
    #. Check DHCP with cirros-dhcpc command on server with sudo
    #. Get node with DHCP agent for network
    #. Ban DHCP agent for the node with pcs
    #. Wait for DHCP agent becoming dead
    #. Check that killed dhcp-agent does not in dhcp-agents list
        for network
    #. Repeat last 4 steps if ban_count is 2
    #. Check that this network is on another health dhcp-agent
    #. Check DHCP with cirros-dhcpc command on server with sudo

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)

    for _ in range(ban_count):
        dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
        nodes_with_dhcp = os_faults_steps.get_nodes_for_agents([dhcp_agent])
        os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                          nodes=nodes_with_dhcp)
        agent_steps.check_alive([dhcp_agent],
                                must_alive=False,
                                timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)
        agent_steps.check_network_rescheduled(
            network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    agent_steps.get_dhcp_agents_for_net(network)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('d14003d7-4cd9-4f68-98e6-c88b8a2ee45d')
def test_ban_all_dhcp_agents_restart_one(network,
                                         floating_ip,
                                         server,
                                         server_steps,
                                         os_faults_steps,
                                         agent_steps,
                                         network_steps):
    """**Scenario:** Ban all DHCP agents and restart the last banned.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Check DHCP with cirros-dhcpc command on server with sudo
    #. Get all existing DHCP agents
    #. Get 2 nodes with DHCP agents for network
    #. Ban 2 DHCP agents for nodes with pcs
    #. Wait for DHCP agents becoming dead
    #. Check that banned dhcp-agents don't in dhcp-agents list
        for network
    #. Get new node with DHCP agent for network
    #. Ban DHCP agent for node with pcs
    #. Wait for DHCP agent becoming dead
    #. Check that banned dhcp-agent is dead
    #. Repeat last 4 steps for all active DHCP agents
    #. Clear the last banned dhcp-agent
    #. Check that cleared dhcp-agent is active
    #. Check that network is on the dhcp-agent which has been cleared
    #. Check DHCP with cirros-dhcpc command on server with sudo
    #. Check that all networks except for external are
        on the cleared dhcp-agent

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)

    networks_on_agents = set()
    for agent in agent_steps.get_agents(binary=config.NEUTRON_DHCP_SERVICE):
        networks_on_agents.update(
            network_steps.get_networks_for_dhcp_agent(agent))

    dhcp_agents_count = len(
        agent_steps.get_agents(binary=config.NEUTRON_DHCP_SERVICE))

    dhcp_agents_for_net = agent_steps.get_dhcp_agents_for_net(network)
    nodes_with_dhcp = os_faults_steps.get_nodes_for_agents(dhcp_agents_for_net)
    os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=nodes_with_dhcp)

    for dhcp_agent in dhcp_agents_for_net:
        agent_steps.check_network_rescheduled(
            network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    for _ in range(dhcp_agents_count - 2):
        dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
        node_with_dhcp = os_faults_steps.get_nodes_for_agents([dhcp_agent])
        os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                          nodes=node_with_dhcp)
        agent_steps.check_alive([dhcp_agent],
                                must_alive=False,
                                timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)

    os_faults_steps.start_service(config.NEUTRON_DHCP_SERVICE,
                                  nodes=node_with_dhcp)
    agent_steps.check_alive([dhcp_agent],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    agent_steps.check_agents_count_for_net(
        network, expected_count=1, timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    server_steps.check_dhcp_on_cirros_server(server)

    networks_count = len(networks_on_agents)
    network_steps.check_nets_count_for_agent(
        dhcp_agent,
        expected_count=networks_count,
        timeout=config.AGENT_RESCHEDULING_TIMEOUT)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('d89b894b-dda2-4156-a4bb-33fff229f54c')
def test_ban_all_dhcp_agents_restart_first(network,
                                           floating_ip,
                                           server,
                                           server_steps,
                                           os_faults_steps,
                                           agent_steps,
                                           network_steps):
    """**Scenario:** Ban all DHCP agents and restart the first banned.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Check DHCP with cirros-dhcpc command on server with sudo
    #. Get free DHCP agents
    #. Get nodes with free DHCP agents
    #. Ban all free DHCP agents for nodes with pcs
    #. Kill all dnsmasq processes for nodes
    #. Wait for DHCP agents becoming dead
    #. Get 2 nodes with DHCP agents for network
    #. Ban 2 DHCP agents for nodes with pcs
    #. Kill all dnsmasq processes for nodes
    #. Wait for DHCP agents becoming dead
    #. Get node for the first banned dhcp-agent
    #. Clear the first banned dhcp-agent
    #. Check that cleared dhcp-agent is active
    #. Check that all dhcp-agents except for the first banned
        don't in dhcp-agents list for network
    #. Check that network is on the dhcp-agent which has been cleared
    #. Check that all networks except for external are
        on the cleared dhcp-agent
    #. Check DHCP with cirros-dhcpc command on server with sudo

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)

    networks_on_agents = set()
    for agent in agent_steps.get_agents(binary=config.NEUTRON_DHCP_SERVICE):
        networks_on_agents.update(
            network_steps.get_networks_for_dhcp_agent(agent))
    free_agents = agent_steps.get_dhcp_agents_not_hosting_net(network)
    nodes_with_free_agents = os_faults_steps.get_nodes_for_agents(free_agents)
    os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=nodes_with_free_agents)
    os_faults_steps.send_signal_to_processes_by_name(
        nodes_with_free_agents,
        name=config.DNSMASQ_SERVICE,
        signal=signal.SIGKILL)
    agent_steps.check_alive(free_agents,
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)

    dhcp_agents_for_net = agent_steps.get_dhcp_agents_for_net(network)
    nodes_with_dhcp = os_faults_steps.get_nodes_for_agents(dhcp_agents_for_net)
    os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=nodes_with_dhcp)
    os_faults_steps.send_signal_to_processes_by_name(
        nodes_with_dhcp,
        name=config.DNSMASQ_SERVICE,
        signal=signal.SIGKILL)
    agent_steps.check_alive(dhcp_agents_for_net,
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)

    agent_to_clear = free_agents[0]
    banned_agents = free_agents[1:] + dhcp_agents_for_net

    node_for_agent = os_faults_steps.get_nodes_for_agents([agent_to_clear])
    os_faults_steps.start_service(config.NEUTRON_DHCP_SERVICE,
                                  nodes=node_for_agent)
    agent_steps.check_alive([agent_to_clear],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    for banned_agent in banned_agents:
        agent_steps.check_network_rescheduled(
            network, banned_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    agent_steps.check_agents_count_for_net(
        network, expected_count=1, timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    networks_count = len(networks_on_agents)
    network_steps.check_nets_count_for_agent(
        agent_to_clear,
        expected_count=networks_count,
        timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('5fea925f-e7a2-4524-80c2-c4f632c304c9')
def test_dhcp_agent_after_drop_rabbit_port(network,
                                           floating_ip,
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
    #. Check DHCP with cirros-dhcpc command on server with sudo
    #. Get node with DHCP agent for network
    #. Drop rabbit's port 5673 using iptables for node from the previous step
    #. Wait for DHCP agent becoming dead
    #. Check that dhcp-agent does not in dhcp-agents list for network
    #. Check that network is on 2 health DHCP-agents
    #. Check DHCP with cirros-dhcpc command on server with sudo
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
    server_steps.attach_floating_ip(server, floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)

    all_dhcp_agents = agent_steps.get_agents(
        binary=config.NEUTRON_DHCP_SERVICE)

    dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
    nodes_with_dhcp = os_faults_steps.get_nodes_for_agents([dhcp_agent])
    os_faults_steps.add_rule_to_drop_port(nodes_with_dhcp, config.RABBIT_PORT)
    agent_steps.check_alive([dhcp_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)
    agent_steps.check_network_rescheduled(
        network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    agent_steps.check_agents_count_for_net(
        network, expected_count=2, timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    server_steps.check_dhcp_on_cirros_server(server)

    os_faults_steps.remove_rule_to_drop_port(nodes_with_dhcp,
                                             config.RABBIT_PORT)
    agent_steps.check_alive(all_dhcp_agents,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('09a8280b-38b2-4414-bc88-665a3843ee6c')
def test_ban_dhcp_agent_many_times(network,
                                   floating_ip,
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
    #. Check DHCP with cirros-dhcpc command on server with sudo
    #. Get nodes with DHCP agents not hosting network
    #. Ban all DHCP agents not hosting network
    #. Wait for banned DHCP agents becoming dead
    #. Get node with DHCP agent for network
    #. Ban DHCP agent for network with pcs
    #. Clear DHCP agent for network with pcs
    #. Repeat last 2 steps 40 times
    #. Check that neutron agent from the previous step is alive
    #. Check that network is on 2 health DHCP-agents
    #. Check DHCP with cirros-dhcpc command on server with sudo

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)

    agent_to_ban = agent_steps.get_dhcp_agents_for_net(network)[0]
    free_agents = agent_steps.get_dhcp_agents_not_hosting_net(network)

    nodes_with_free_agents = os_faults_steps.get_nodes_for_agents(free_agents)
    os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=nodes_with_free_agents)
    agent_steps.check_alive(free_agents,
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)

    node_with_dhcp = os_faults_steps.get_nodes_for_agents([agent_to_ban])
    for _ in range(40):
        os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                          nodes=node_with_dhcp)
        os_faults_steps.start_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=node_with_dhcp)

    agent_steps.check_alive([agent_to_ban],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    agent_steps.check_agents_count_for_net(
        network, expected_count=2, timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id(
    'd794afda-4e3e-422d-80be-525e6517d625',
    controller_cmd=config.FUEL_PRIMARY_CONTROLLER_CMD)
@pytest.mark.idempotent_id(
    '221c4299-4ba6-4257-9f65-b280e2b69eb4',
    controller_cmd=config.FUEL_NON_PRIMARY_CONTROLLERS_CMD)
@pytest.mark.parametrize('controller_cmd',
                         [config.FUEL_PRIMARY_CONTROLLER_CMD,
                          config.FUEL_NON_PRIMARY_CONTROLLERS_CMD],
                         ids=['primary', 'non_primary'])
def test_destroy_controller_check_dhcp(network,
                                       server,
                                       floating_ip,
                                       get_network_steps,
                                       server_steps,
                                       os_faults_steps,
                                       agent_steps,
                                       controller_cmd):
    """**Scenario:** Destroy controller and check DHCP.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Get primary/non-primary controller
    #. Get DHCP agent for primary/non-primary controller node
    #. Reschedule network to DHCP agent on primary/non-primary
        controller if it is not there yet
    #. Check DHCP with cirros-dhcpc command on server with sudo
    #. Destroy primary/non-primary controller
    #. Wait for neutron availability
    #. Wait for primary/non-primary controller's DHCP agent becoming dead
    #. Check that dhcp-agent does not in dhcp-agents list for network
    #. Check that network is on 2 healthy agents
    #. Check that all networks rescheduled from primary/non-primary
        controller
    #. Check DHCP with cirros-dhcpc command on server with sudo

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, floating_ip)
    controller = os_faults_steps.get_node_by_cmd(controller_cmd)
    dhcp_agent = agent_steps.get_agents(node=controller,
                                        binary=config.NEUTRON_DHCP_SERVICE)[0]
    agent_steps.reschedule_network_to_dhcp_agent(
        dhcp_agent, network, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    server_steps.check_dhcp_on_cirros_server(server)

    os_faults_steps.poweroff_nodes(controller)
    # wait for neutron availability and refresh network_steps
    network_steps = get_network_steps()

    agent_steps.check_alive([dhcp_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)
    agent_steps.check_network_rescheduled(
        network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    agent_steps.check_agents_count_for_net(
        network, expected_count=2, timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    network_steps.check_nets_count_for_agent(
        dhcp_agent,
        expected_count=0,
        timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('eac820d1-a4b4-43da-a8c6-4514f20300d1')
def test_dhcp_alive_after_primary_controller_reset(network,
                                                   server,
                                                   floating_ip,
                                                   get_network_steps,
                                                   server_steps,
                                                   os_faults_steps,
                                                   agent_steps):
    """**Scenario:** Reset primary controller and check DHCP is alive.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Get primary controller
    #. Get DHCP agent for primary controller node
    #. Reschedule network to DHCP agent on primary controller
        if it is not there yet
    #. Check DHCP with cirros-dhcpc command on server with sudo
    #. Reset primary controller
    #. Wait for neutron availability
    #. Wait for primary controller's DHCP agent becoming dead
    #. Check that dhcp-agent does not in dhcp-agents list for network
    #. Check that all networks rescheduled from primary controller
    #. Check DHCP with cirros-dhcpc command on server with sudo

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, floating_ip)
    primary_controller = os_faults_steps.get_node_by_cmd(
        config.FUEL_PRIMARY_CONTROLLER_CMD)
    dhcp_agent = agent_steps.get_agents(node=primary_controller,
                                        binary=config.NEUTRON_DHCP_SERVICE)[0]
    agent_steps.reschedule_network_to_dhcp_agent(
        dhcp_agent, network, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    server_steps.check_dhcp_on_cirros_server(server)

    os_faults_steps.reset_nodes(primary_controller)
    # wait for neutron availability and refresh network_steps
    network_steps = get_network_steps()

    agent_steps.check_alive([dhcp_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)
    agent_steps.check_network_rescheduled(
        network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    network_steps.check_nets_count_for_agent(
        dhcp_agent,
        expected_count=0,
        timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('72634b22-f7a2-454b-a0a0-11298eb44a80',
                           agents_count_for_net=1)
@pytest.mark.idempotent_id('1eb0169c-a7e4-48bb-a68c-1aa554ef26a2',
                           agents_count_for_net=3)
@pytest.mark.parametrize('set_dhcp_agents_count_for_net, agents_count_for_net',
                         [(1, 1), (3, 3)],
                         ids=['1_agent_for_net', '3_agents_for_net'],
                         indirect=['set_dhcp_agents_count_for_net'])
@pytest.mark.usefixtures('set_dhcp_agents_count_for_net')
def test_change_default_dhcp_agents_count_for_net(
        network,
        server,
        floating_ip,
        server_steps,
        os_faults_steps,
        agent_steps,
        agents_count_for_net):
    """**Scenario:** Change default DHCP agents count for network.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Check DHCP with cirros-dhcpc command on server with sudo
    #. Check that agents count is the same as expected
    #. Get all DHCP agents count
    #. Get node with DHCP agent for network
    #. Ban DHCP agent for node with pcs
    #. Wait for DHCP agent becoming dead
    #. Check that banned dhcp-agent doesn't in dhcp-agents list
        for network
    #. Check that agents count equals to the value from config or to
        free agents count
    #. Repeat last 5 steps for all active DHCP agents except for one
    #. Get node with DHCP agent for network
    #. Ban DHCP agent for node with pcs
    #. Wait for DHCP agent becoming dead
    #. Clear the last banned dhcp-agent
    #. Check that cleared dhcp-agent is active
    #. Check that network is on the one dhcp-agent which has been cleared
    #. Check DHCP with cirros-dhcpc command on server with sudo

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)
    agent_steps.check_agents_count_for_net(
        network, expected_count=agents_count_for_net,
        timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    dhcp_agents_count = len(
        agent_steps.get_agents(binary=config.NEUTRON_DHCP_SERVICE))

    for free_agents_count in range(dhcp_agents_count, 1, - 1):
        dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
        node_with_dhcp = os_faults_steps.get_nodes_for_agents([dhcp_agent])
        os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                          nodes=node_with_dhcp)
        agent_steps.check_alive([dhcp_agent],
                                must_alive=False,
                                timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)
        agent_steps.check_network_rescheduled(
            network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

        expected_count = min(agents_count_for_net, free_agents_count - 1)
        agent_steps.check_agents_count_for_net(
            network, expected_count=expected_count,
            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
    node_with_dhcp = os_faults_steps.get_nodes_for_agents([dhcp_agent])
    os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=node_with_dhcp)
    agent_steps.check_alive([dhcp_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)

    os_faults_steps.start_service(config.NEUTRON_DHCP_SERVICE,
                                  nodes=node_with_dhcp)
    agent_steps.check_alive([dhcp_agent],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    agent_steps.check_agents_count_for_net(
        network, expected_count=1, timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('a771c0e1-58c0-4b44-8fe2-a3d557504751')
def test_kill_check_dhcp_agents(network,
                                floating_ip,
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
    server_steps.attach_floating_ip(server, floating_ip)
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
    agent_steps.check_agents_count_for_net(
        network, expected_count=2, timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    dhcp_agents = agent_steps.get_dhcp_agents_for_net(network)
    agent_steps.check_alive(dhcp_agents,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.idempotent_id('f103c8aa-b5b0-42bd-a173-55ca669193ee')
@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
def test_manually_rescheduling_dhcp_agent(network,
                                          floating_ip,
                                          server,
                                          server_steps,
                                          port_steps,
                                          agent_steps):
    """**Scenario:** Manually reschedule dhcp-agent.

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
    #. Check ports on net
    #. Reschedule network from DHCP agent
    #. Check that the network is moved from this dhcp-agent
    #. Set network to another dhcp-agent
    #. Check that the network moved to this dhcp-agent
    #. Check that ports haven't been changed

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)
    dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
    dhcp_agent_second = agent_steps.get_dhcp_agents_not_hosting_net(network)[0]
    ports = port_steps.get_ports(
        device_owner=config.PORT_DEVICE_OWNER_DHCP, network_id=network['id'])
    agent_steps.remove_network_from_dhcp_agent(dhcp_agent, network)
    agent_steps.add_network_to_dhcp_agent(dhcp_agent_second, network)
    agent_steps.check_network_is_on_agent(
        network, dhcp_agent_second, timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    new_ports = port_steps.get_ports(
        device_owner=config.PORT_DEVICE_OWNER_DHCP, network_id=network['id'])
    port_steps.check_equal_ports(ports_1=ports, ports_2=new_ports)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('1ea3a2e0-f46f-4d10-b37f-27631bb8a1e2')
@pytest.mark.parametrize(
    'change_neutron_quota',
    [dict(network=50, router=50, subnet=50, port=200)],
    indirect=True)
@pytest.mark.usefixtures('change_neutron_quota')
def test_check_nets_count_for_agents_nearly_equals(
        router,
        create_max_networks_with_instances,
        network_steps,
        agent_steps):
    """**Scenario:** Check that nets count for DHCP agents nearly equals.

    **Setup:**

    #. Increase neutron quotas
    #. Create cirros image
    #. Create flavor
    #. Create security group

    **Steps:**

    #. Create max possible count of networks, connect all networks
        to router with external network
    #. Create and delete server for each network
    #. Check that quantity of nets on DHCP agents is nearly the same

    **Teardown:**

    #. Delete all created networks, subnets and router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    create_max_networks_with_instances(router)

    # max difference between max and min values for nets count
    # for agents 50% is OK according to the author of scenario
    max_difference_in_percent = 50
    all_dhcp_agents = agent_steps.get_agents(
        binary=config.NEUTRON_DHCP_SERVICE)

    network_steps.check_nets_count_difference_for_agents(
        all_dhcp_agents,
        max_difference_in_percent)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('3952df20-88df-4755-b6c6-3baad7686ec2')
@pytest.mark.parametrize(
    'change_neutron_quota',
    [dict(network=50, router=50, subnet=50, port=200)],
    indirect=True)
@pytest.mark.usefixtures('change_neutron_quota')
def test_check_port_binding_after_node_restart(
        router,
        create_max_networks_with_instances,
        get_neutron_client,
        port_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Check port binding after node restart.

    **Note:**
        This test verifies bug #1501070

    **Setup:**

    #. Increase neutron quotas
    #. Create cirros image
    #. Create flavor
    #. Create security group

    **Steps:**

    #. Create max possible count of networks, connect all networks
        to router with external network
    #. Create and delete server for each network
    #. Check ports on the first network
    #. Check host binding for all ports
    #. Get DHCP agent for the first network
    #. Get node with DHCP agent for network
    #. Destroy node with DHCP agent
    #. Wait for neutron availability
    #. Wait for DHCP agent becoming dead
    #. Start node with DHCP agent
    #. Wait for DHCP agent becoming alive
    #. Check ports on network
    #. Check that ports ids are the same as before destroying node
    #. Check that network rescheduled from one DHCP agent to another
         and only one host binding changed after restart.

    **Teardown:**

    #. Delete all created networks, subnets and router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    network = create_max_networks_with_instances(router)[0]

    ports_before = port_steps.get_ports(
        device_owner=config.PORT_DEVICE_OWNER_DHCP, network_id=network['id'])

    dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
    nodes_with_dhcp = os_faults_steps.get_nodes_for_agents([dhcp_agent])

    os_faults_steps.poweroff_nodes(nodes_with_dhcp)
    # wait for neutron availability
    get_neutron_client()

    agent_steps.check_alive([dhcp_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)

    os_faults_steps.poweron_nodes(nodes_with_dhcp)
    agent_steps.check_alive([dhcp_agent],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    ports_after = port_steps.get_ports(
        device_owner=config.PORT_DEVICE_OWNER_DHCP, network_id=network['id'])
    port_steps.check_ports_ids_equal(ports_before, ports_after)
    port_steps.check_ports_binding_difference(ports_before,
                                              ports_after,
                                              expected_removed_count=1,
                                              expected_added_count=1)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('5bc6c902-961a-4bd4-9fd4-0471dddd6f1c')
@pytest.mark.parametrize(
    'change_neutron_quota',
    [dict(network=50, router=50, subnet=50, port=200)],
    indirect=True)
@pytest.mark.usefixtures('change_neutron_quota')
def test_check_dhcp_agents_for_net_after_restart(
        router,
        create_max_networks_with_instances,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Check dhcp-agents assinged to network after restart.

    **Note:**
        This test verifies bug #1506198

    **Setup:**

    #. Increase neutron quotas
    #. Create cirros image
    #. Create flavor
    #. Create security group

    **Steps:**

    #. Create max possible count of networks, connect all networks
        to router with external network
    #. Create and delete server for each network
    #. Check DHCP agents count for the first network
    #. Get all nodes with DHCP agents
    #. Disable all DHCP agents
    #. Wait for DHCP agents becoming dead
    #. Enable all DHCP agents
    #. Wait for DHCP agents becoming alive
    #. Check that DHCP agents count for the first network is the same
        as before restart

    **Teardown:**

    #. Delete all created networks, subnets and router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    network = create_max_networks_with_instances(router)[0]
    net_dhcp_agents = agent_steps.get_dhcp_agents_for_net(network)
    initial_count = len(net_dhcp_agents)

    agent_steps.check_agents_count_for_net(
        network, expected_count=initial_count,
        timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    all_dhcp_agents = agent_steps.get_agents(
        binary=config.NEUTRON_DHCP_SERVICE)
    nodes_with_dhcp = os_faults_steps.get_nodes_for_agents(all_dhcp_agents)
    os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=nodes_with_dhcp)
    agent_steps.check_alive(all_dhcp_agents,
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)

    os_faults_steps.start_service(config.NEUTRON_DHCP_SERVICE,
                                  nodes=nodes_with_dhcp)
    agent_steps.check_alive(all_dhcp_agents,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    agent_steps.check_agents_count_for_net(
        network, expected_count=initial_count,
        timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('6890121c-73b6-42e5-b358-ed7037b36184')
@pytest.mark.parametrize(
    'change_neutron_quota',
    [dict(network=50, router=50, subnet=50, port=200)],
    indirect=True)
@pytest.mark.usefixtures('change_neutron_quota')
def test_check_tap_interfaces_for_net_after_restart(
        router,
        create_max_networks_with_instances,
        port_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Check all taps ids are unique after DHCP agents restart.

    **Note:**
        This test verifies bug #1499914

    **Setup:**

    #. Increase neutron quotas
    #. Create cirros image
    #. Create flavor
    #. Create security group

    **Steps:**

    #. Create max possible count of networks, connect all networks
        to router with external network
    #. Create and delete server for each network
    #. Get all DHCP ports
    #. Get all nodes with DHCP agents
    #. Disable all DHCP agents
    #. Wait for DHCP agents becoming dead
    #. Make all DHCP ports 'reserved_dhcp_port'
    #. Enable all DHCP agents
    #. Wait for DHCP agents becoming alive
    #. Check all taps ids are unique for all networks on all controllers

    **Teardown:**

    #. Delete all created networks, subnets and router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    networks = create_max_networks_with_instances(router)
    controller = os_faults_steps.get_node(
        service_names=[config.NEUTRON_DHCP_SERVICE])
    dhcp_ports = port_steps.get_ports(
        device_owner=config.PORT_DEVICE_OWNER_DHCP)

    all_dhcp_agents = agent_steps.get_agents(
        binary=config.NEUTRON_DHCP_SERVICE)
    nodes_with_dhcp = os_faults_steps.get_nodes_for_agents(all_dhcp_agents)

    os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=nodes_with_dhcp)
    agent_steps.check_alive(all_dhcp_agents,
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)

    os_faults_steps.delete_ports_bindings_for_dhcp_agents(controller)
    for dhcp_port in dhcp_ports:
        port_steps.update(dhcp_port,
                          device_id=config.PORT_DEVICE_ID_RESERVED_DHCP)

    os_faults_steps.start_service(config.NEUTRON_DHCP_SERVICE,
                                  nodes=nodes_with_dhcp)
    agent_steps.check_alive(all_dhcp_agents,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    for network in networks:
        os_faults_steps.check_tap_interfaces_are_unique(
            nodes_with_dhcp, network, timeout=config.TAP_INTERFACE_UP_TIMEOUT)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3",
                      "l3_agent_nodes_count >= 3",
                      "not l3_ha and not dvr")
@pytest.mark.idempotent_id('ce6dcbbe-583e-495e-b41a-084ccc8dff94')
@pytest.mark.parametrize(
    'change_neutron_quota',
    [dict(network=50, router=50, subnet=50, port=200)],
    indirect=True)
@pytest.mark.usefixtures('change_neutron_quota')
def test_ban_two_dhcp_and_two_l3_agents(router,
                                        create_max_networks_with_instances,
                                        agent_steps,
                                        os_faults_steps):
    """**Scenario:** Ban two DHCP and L3 agents and check logs.

    **Note:**
        This test verifies bug #1493754 and #1651442

    **Setup:**

    #. Increase neutron quotas
    #. Create cirros image
    #. Create flavor
    #. Create security group

    **Steps:**

    #. Get all controllers
    #. Get the last line number for neutron server log for all controllers
    #. Create max possible count of networks, connect all networks
        to router with external network
    #. Create and delete server for each network
    #. Get nodes with DHCP agents for network
    #. Ban DHCP agents for nodes with pcs
    #. Wait for DHCP agents becoming dead
    #. Check that banned dhcp-agents don't in dhcp-agents list
        for network
    #. Get node with l3 agent for router
    #. Ban l3 agent for the node with pcs
    #. Wait for l3 agent becoming dead
    #. Repeat last 3 steps once
    #. Check that router rescheduled from l3 agents
    #. Check there are no new ERROR logs in neutron-server log files

    **Teardown:**

    #. Delete all created networks, subnets and router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    dhcp_agents = agent_steps.get_agents(binary=config.NEUTRON_DHCP_SERVICE)
    controllers = os_faults_steps.get_nodes_for_agents(dhcp_agents)

    log_file = config.AGENT_LOGS[config.NEUTRON_SERVER_SERVICE][0]
    line_count_file_path = os_faults_steps.store_file_line_count(controllers,
                                                                 log_file)

    network = create_max_networks_with_instances(router)[0]

    net_dhcp_agents = agent_steps.get_dhcp_agents_for_net(network)
    nodes_with_dhcp = os_faults_steps.get_nodes_for_agents(net_dhcp_agents)
    os_faults_steps.terminate_service(config.NEUTRON_DHCP_SERVICE,
                                      nodes=nodes_with_dhcp)
    agent_steps.check_alive(net_dhcp_agents,
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)
    for dhcp_agent in net_dhcp_agents:
        agent_steps.check_network_rescheduled(
            network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    l3_agents = []
    for _ in range(2):
        l3_agent = agent_steps.get_l3_agents_for_router(router)[0]
        node_with_l3 = os_faults_steps.get_nodes_for_agents([l3_agent])

        os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE,
                                          nodes=node_with_l3)
        agent_steps.check_alive([l3_agent],
                                must_alive=False,
                                timeout=config.NEUTRON_AGENT_DIE_TIMEOUT)
        l3_agents.append(l3_agent)
    for l3_agent in l3_agents:
        agent_steps.check_router_rescheduled(
            router,
            l3_agent,
            timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    os_faults_steps.check_string_in_file(
        controllers,
        file_name=log_file,
        keyword=config.STR_ERROR,
        non_matching=config.STR_NEUTRON_API_V2_ERROR,
        start_line_number_file=line_count_file_path,
        must_present=False)
