"""
-------------------
Neutron L3 HA tests
-------------------
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

pytestmark = [
    pytest.mark.destructive,
    pytest.mark.requires("l3_ha", "l3_agent_nodes_count >= 3")
]


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('ee080cc2-b658-42cf-ac0b-f5eab906fcf5', ban_count=1)
@pytest.mark.idempotent_id('f48dc010-f4d1-464b-aa73-834a706569e6', ban_count=2)
@pytest.mark.parametrize(
    'neutron_2_networks', ['different_routers'], indirect=True)
@pytest.mark.parametrize('ban_count', [1, 2])
def test_ban_l3_agent_with_active_ha_state_for_router(
        neutron_2_servers_different_networks,
        nova_create_floating_ip,
        server_steps,
        agent_steps,
        os_faults_steps,
        ban_count):
    """**Scenario:** Ban l3-agent with ACTIVE ha_state for router.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create network_2 with subnet_2 and router_2
    #. Create server_1
    #. Create server_2 on another compute and connect it to network_2

    **Steps:**

    #. Create and attach floating IP for each server
    #. Get L3 agent with ACTIVE ha_state for router_1
    #. Start ping between servers with floating IP
    #. Ban ACTIVE L3 agent
    #. Wait for another L3 agent becomes ACTIVE
    #. Repeat last 2 steps ``ban_count`` times
    #. Check that ping loss is not more than 10 * ``ban_count`` packets

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, router
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers
    router_1 = neutron_2_servers_different_networks.routers[0]
    floating_ip_1 = nova_create_floating_ip()
    floating_ip_2 = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_1, floating_ip_1)
    server_steps.attach_floating_ip(server_2, floating_ip_2)
    with server_steps.get_server_ssh(server_1) as server_ssh:
        with server_steps.check_ping_loss_context(
                floating_ip_2.ip,
                max_loss=config.NEUTRON_L3_HA_RESTART_MAX_PING_LOSS *
                ban_count,
                server_ssh=server_ssh):
            for _ in range(ban_count):
                agent = agent_steps.get_l3_agents_for_router(
                    router_1, filter_attrs=config.HA_STATE_ACTIVE_ATTRS)[0]
                agent_node = os_faults_steps.get_nodes_for_l3_agents([agent])
                os_faults_steps.terminate_service(
                    config.NEUTRON_L3_SERVICE, nodes=agent_node)
                agent_steps.check_l3_ha_router_rescheduled(
                    router_1,
                    old_l3_agent=agent,
                    timeout=config.L3_AGENT_RESCHEDULING_TIMEOUT)


@pytest.mark.idempotent_id('df236e04-e743-4c3d-94ca-d76e0183b509')
def test_ban_l3_agent_with_ping_public_ip(
        router,
        server,
        nova_floating_ip,
        server_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Ban l3-agent with ACTIVE ha_state for router during ping.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create server
    #. Create floating ip

    **Steps:**

    #. Attach floating IP to server
    #. Get L3 agent with ACTIVE ha_state for router
    #. Start ping from server to public ip
    #. Ban ACTIVE L3 agent
    #. Wait for another L3 agent becomes ACTIVE
    #. Check that ping loss is not more than 40 packets

    **Teardown:**

    #. Delete server
    #. Delete network, subnet, router
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    agent = agent_steps.get_l3_agents_for_router(
        router, filter_attrs=config.HA_STATE_ACTIVE_ATTRS)[0]
    agent_node = os_faults_steps.get_nodes_for_l3_agents([agent])

    server_steps.attach_floating_ip(server, nova_floating_ip)
    with server_steps.get_server_ssh(server) as server_ssh:
        with server_steps.check_ping_loss_context(
                config.GOOGLE_DNS_IP,
                max_loss=config.NEUTRON_L3_HA_RESTART_MAX_PING_LOSS,
                server_ssh=server_ssh):
            os_faults_steps.terminate_service(
                config.NEUTRON_L3_SERVICE, nodes=agent_node)
            agent_steps.check_l3_ha_router_rescheduled(
                router,
                old_l3_agent=agent,
                timeout=config.L3_AGENT_RESCHEDULING_TIMEOUT)


@pytest.mark.idempotent_id('dd0de43b-6aae-4731-8383-05987c539cde')
def test_delete_ns_for_router_on_node_with_active_ha_state(
        router,
        server,
        nova_floating_ip,
        server_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Delete namespace for router on node with ACTIVE ha_state.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create server
    #. Create floating ip

    **Steps:**

    #. Attach floating IP to server
    #. Get L3 agent with ACTIVE ha_state for router
    #. Start ping from server to public ip
    #. Delete router namespace on node with active L3 agent
    #. Check that ping loss is not more than 40 packets

    **Teardown:**

    #. Delete server
    #. Delete network, subnet, router
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    agent = agent_steps.get_l3_agents_for_router(
        router, filter_attrs=config.HA_STATE_ACTIVE_ATTRS)[0]
    agent_node = os_faults_steps.get_nodes_for_l3_agents([agent])

    server_steps.attach_floating_ip(server, nova_floating_ip)

    with server_steps.get_server_ssh(server) as server_ssh:
        with server_steps.check_ping_loss_context(
                config.GOOGLE_DNS_IP,
                max_loss=config.NEUTRON_L3_HA_RESTART_MAX_PING_LOSS,
                server_ssh=server_ssh):
            os_faults_steps.delete_router_namespace(nodes=agent_node,
                                                    router=router)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('e0f0c2e9-7895-4ca6-87a3-ff67f2503477')
@pytest.mark.parametrize(
    'neutron_2_networks', ['different_routers'], indirect=True)
def test_destroy_primary_controller(
        neutron_2_servers_different_networks,
        nova_create_floating_ip,
        reschedule_router_active_l3_agent,
        server_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Destroy primary controller.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create network_2 with subnet_2 and router_2
    #. Create server_1
    #. Create server_2 on another compute and connect it to network_2

    **Steps:**

    #. Create and attach floating IP for each server
    #. Get L3 agent with ACTIVE ha_state for router_1
    #. Get primary controller
    #. Reschedule router's active L3 agent to primary controller
    #. Start ping between servers with floating IP
    #. Destroy primary controller
    #. Check that ping loss is not more than 40 packets

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, router
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers
    floating_ip_1 = nova_create_floating_ip()
    floating_ip_2 = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_1, floating_ip_1)
    server_steps.attach_floating_ip(server_2, floating_ip_2)

    primary_controller = os_faults_steps.get_nodes_by_cmd(
        config.FUEL_PRIMARY_CONTROLLER_CMD)
    router_1 = neutron_2_servers_different_networks.routers[0]
    reschedule_router_active_l3_agent(router_1, primary_controller)

    with server_steps.get_server_ssh(server_1) as server_ssh:
        with server_steps.check_ping_loss_context(
                floating_ip_2.ip,
                max_loss=config.NEUTRON_L3_HA_RESTART_MAX_PING_LOSS,
                server_ssh=server_ssh):
            os_faults_steps.poweroff_nodes(primary_controller)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('b87ec554-d369-4615-9dd5-41b590856766')
@pytest.mark.parametrize(
    'neutron_2_networks', ['different_routers'], indirect=True)
def test_destroy_non_primary_controller(
        neutron_2_servers_different_networks,
        nova_create_floating_ip,
        reschedule_router_active_l3_agent,
        server_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Destroy non primary controller.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create network_2 with subnet_2 and router_2
    #. Create server_1
    #. Create server_2 on another compute and connect it to network_2

    **Steps:**

    #. Create and attach floating IP for each server
    #. Get L3 agent with ACTIVE ha_state for router_1
    #. Get primary controller
    #. Reschedule router's active L3 agent to non primary controller
    #. Start ping between servers with floating IP
    #. Destroy node with L3 agent for router_1 with ACTIVE ha_state
    #. Check that ping loss is not more than 40 packets

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, router
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers
    floating_ip_1 = nova_create_floating_ip()
    floating_ip_2 = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_1, floating_ip_1)
    server_steps.attach_floating_ip(server_2, floating_ip_2)

    primary_controller = os_faults_steps.get_nodes_by_cmd(
        config.FUEL_PRIMARY_CONTROLLER_CMD)
    l3_agent_nodes = os_faults_steps.get_nodes(
        service_names=[config.NEUTRON_L3_SERVICE])

    router_1 = neutron_2_servers_different_networks.routers[0]
    reschedule_router_active_l3_agent(router_1,
                                      l3_agent_nodes - primary_controller)

    agent = agent_steps.get_l3_agents_for_router(
        router_1, filter_attrs=config.HA_STATE_ACTIVE_ATTRS)[0]
    agent_node = os_faults_steps.get_nodes_for_l3_agents([agent])

    with server_steps.get_server_ssh(server_1) as server_ssh:
        with server_steps.check_ping_loss_context(
                floating_ip_2.ip,
                max_loss=config.NEUTRON_L3_HA_RESTART_MAX_PING_LOSS,
                server_ssh=server_ssh):
            os_faults_steps.poweroff_nodes(agent_node)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('d796d59b-2cb3-447a-acf7-d7072312f877')
@pytest.mark.parametrize(
    'neutron_2_networks', ['different_routers'], indirect=True)
def test_reset_primary_controller(
        neutron_2_servers_different_networks,
        nova_create_floating_ip,
        reschedule_router_active_l3_agent,
        server_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Reset primary controller.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create network_2 with subnet_2 and router_2
    #. Create server_1
    #. Create server_2 on another compute and connect it to network_2

    **Steps:**

    #. Create and attach floating IP for each server
    #. Get L3 agent with ACTIVE ha_state for router_1
    #. Get primary controller
    #. Reschedule router's active L3 agent to primary controller
    #. Start ping between servers with floating IP
    #. Reset primary controller
    #. Check that ping loss is not more than 40 packets

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, router
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers
    floating_ip_1 = nova_create_floating_ip()
    floating_ip_2 = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_1, floating_ip_1)
    server_steps.attach_floating_ip(server_2, floating_ip_2)

    primary_controller = os_faults_steps.get_nodes_by_cmd(
        config.FUEL_PRIMARY_CONTROLLER_CMD)
    router_1 = neutron_2_servers_different_networks.routers[0]
    reschedule_router_active_l3_agent(router_1, primary_controller)

    with server_steps.get_server_ssh(server_1) as server_ssh:
        with server_steps.check_ping_loss_context(
                floating_ip_2.ip,
                max_loss=config.NEUTRON_L3_HA_RESTART_MAX_PING_LOSS,
                server_ssh=server_ssh):
            os_faults_steps.reset_nodes(primary_controller)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('8830caf4-5931-469b-bc7c-55ccdfdb3723')
@pytest.mark.parametrize(
    'neutron_2_networks', ['different_routers'], indirect=True)
def test_disable_all_l3_agents_and_enable_them(
        neutron_2_servers_diff_nets_with_floating,
        server_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Disable all l3 agents and enable them.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create network_2 with subnet_2 and router_2
    #. Create server_1
    #. Create server_2 on another compute and connect it to network_2

    **Steps:**

    #. Create and attach floating IP for each server
    #. Start ping between servers with floating IP
    #. Ban all L3 agents
    #. Wait for all L3 agents to be died
    #. Clear all L3 agents
    #. Wait for all L3 agents to be alive
    #. Check that ping loss is not more than 100 packets

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_1, server_2 = neutron_2_servers_diff_nets_with_floating.servers
    floating_ip_2 = neutron_2_servers_diff_nets_with_floating.floating_ips[1]

    l3_agents = agent_steps.get_agents(binary=config.NEUTRON_L3_SERVICE)
    nodes_with_l3 = os_faults_steps.get_nodes_for_l3_agents(l3_agents)

    with server_steps.get_server_ssh(server_1) as server_ssh:
        with server_steps.check_ping_loss_context(
                floating_ip_2.ip,
                max_loss=config.NEUTRON_L3_HA_RESTART_MAX_PING_LOSS,
                server_ssh=server_ssh):
            os_faults_steps.terminate_service(
                config.NEUTRON_L3_SERVICE, nodes=nodes_with_l3)
            agent_steps.check_alive(
                l3_agents,
                must_alive=False,
                timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

            os_faults_steps.start_service(
                config.NEUTRON_L3_SERVICE, nodes=nodes_with_l3)
            agent_steps.check_alive(
                l3_agents, timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
