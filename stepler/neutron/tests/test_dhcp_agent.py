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


pytestmark = [pytest.mark.requires("computes_count >= 2 and vlan"),
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


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('d14003d7-4cd9-4f68-98e6-c88b8a2ee45d')
def test_ban_all_dhcp_agents_restart_one(network,
                                         nova_floating_ip,
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
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)

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
                                timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    os_faults_steps.start_service(config.NEUTRON_DHCP_SERVICE,
                                  nodes=node_with_dhcp)
    agent_steps.check_alive([dhcp_agent],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    agent_steps.check_agents_count_for_net(network, expected_count=1)
    server_steps.check_dhcp_on_cirros_server(server)

    networks_count = len(
        network_steps.get_networks(**{config.EXTERNAL_ROUTER: False}))
    network_steps.check_nets_count_for_agent(dhcp_agent,
                                             expected_count=networks_count)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('d89b894b-dda2-4156-a4bb-33fff229f54c')
def test_ban_all_dhcp_agents_restart_first(network,
                                           nova_floating_ip,
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
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)

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
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

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
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

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

    agent_steps.check_agents_count_for_net(network, expected_count=1)
    networks_count = len(
        network_steps.get_networks(**{config.EXTERNAL_ROUTER: False}))
    network_steps.check_nets_count_for_agent(agent_to_clear,
                                             expected_count=networks_count)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
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
                                       nova_floating_ip,
                                       server_steps,
                                       os_faults_steps,
                                       network_steps,
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
    #. Wait for primary/non-primary controller's DHCP agent becoming dead
    #. Check that dhcp-agent does not in dhcp-agents list for network
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
    server_steps.attach_floating_ip(server, nova_floating_ip)
    controller = os_faults_steps.get_node_by_cmd(controller_cmd)
    dhcp_agent = agent_steps.get_agents(node=controller,
                                        binary=config.NEUTRON_DHCP_SERVICE)[0]
    agent_steps.reschedule_network_to_dhcp_agent(
        dhcp_agent, network, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    server_steps.check_dhcp_on_cirros_server(server)

    os_faults_steps.poweroff_nodes(controller)
    agent_steps.check_alive([dhcp_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    agent_steps.check_network_rescheduled(
        network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    network_steps.check_nets_count_for_agent(dhcp_agent,
                                             expected_count=0)
    server_steps.check_dhcp_on_cirros_server(server)


@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('eac820d1-a4b4-43da-a8c6-4514f20300d1')
def test_dhcp_alive_after_primary_controller_reset(network,
                                                   server,
                                                   nova_floating_ip,
                                                   server_steps,
                                                   os_faults_steps,
                                                   network_steps,
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
    server_steps.attach_floating_ip(server, nova_floating_ip)
    primary_controller = os_faults_steps.get_node_by_cmd(
        config.FUEL_PRIMARY_CONTROLLER_CMD)
    dhcp_agent = agent_steps.get_agents(node=primary_controller,
                                        binary=config.NEUTRON_DHCP_SERVICE)[0]
    agent_steps.reschedule_network_to_dhcp_agent(
        dhcp_agent, network, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    server_steps.check_dhcp_on_cirros_server(server)

    os_faults_steps.reset_nodes(primary_controller)
    agent_steps.check_alive([dhcp_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    agent_steps.check_network_rescheduled(
        network, dhcp_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    network_steps.check_nets_count_for_agent(dhcp_agent,
                                             expected_count=0)
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


@pytest.mark.idempotent_id('f103c8aa-b5b0-42bd-a173-55ca669193ee')
@pytest.mark.requires("dhcp_agent_nodes_count >= 3")
def test_manually_rescheduling_dhcp_agent(network,
                                          nova_floating_ip,
                                          server,
                                          server_steps,
                                          port_steps,
                                          ports,
                                          agent_steps):
    """**Scenario:** Manually rescheduling dhcp-agent.

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
    #. Set network to other dhcp-agent
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
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.check_dhcp_on_cirros_server(server)
    dhcp_agent = agent_steps.get_dhcp_agents_for_net(network)[0]
    ports = port_steps.get_ports(
        device_owner=config.PORT_DEVICE_OWNER_DHCP, device_id=network['id'])
    agent_steps.remove_network_from_dhcp_agent(network, dhcp_agent)
    agent_steps.add_network_to_dhcp_agent(network, dhcp_agent)
    agent_steps.check_alive([dhcp_agent],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    new_ports = port_steps.get_ports(
        device_owner=config.PORT_DEVICE_OWNER_DHCP, device_id=network['id'])
    port_steps.compare_ports(ports_1=ports, ports_2=new_ports)
