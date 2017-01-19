"""
-------------------------
Neutron OVS restart tests
-------------------------
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

pytestmark = pytest.mark.destructive


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('ee080cc2-b658-42cf-ac0b-f5eab906fcf5')
def test_restart_with_pcs_disable_enable(
        neutron_2_servers_different_networks,
        nova_floating_ip,
        server_steps,
        os_faults_steps):
    """**Scenario:** Restart OVS-agents with pcs disable/enable on controllers.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router
    #. Create server_1
    #. Create floating ip
    #. Create network_2 with subnet_2
    #. Add network_2 interface to router
    #. Create server_2 on another compute and connect it to network_2

    **Steps:**

    #. Attach floating IP to server_1
    #. Check ping from server_1 to server_2
    #. Restart ovs-agents with pcs enable/disable on controllers
    #. Check ping from server_1 to server_2

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, router
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_fixed_ip = server_steps.get_fixed_ip(server_2)

    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            server_2_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    os_faults_steps.restart_services([config.NEUTRON_OVS_SERVICE])

    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            server_2_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('310c630d-38f0-402b-9423-ffb14fb766b2')
def test_restart_with_pcs_ban_clear(
        neutron_2_servers_different_networks,
        nova_floating_ip,
        server_steps,
        os_faults_steps):
    """**Scenario:** Restart OVS-agents with pcs ban/clear on controllers.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router
    #. Create server_1
    #. Create floating ip
    #. Create network_2 with subnet_2
    #. Add network_2 interface to router
    #. Create server_2 on another compute and connect it to network_2

    **Steps:**

    #. Attach floating IP to server_1
    #. Check ping from server_1 to server_2
    #. Restart ovs-agents with pcs ban/clear on controllers
    #. Check ping from server_1 to server_2

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, router
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_fixed_ip = server_steps.get_fixed_ip(server_2)

    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            server_2_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    nodes = os_faults_steps.get_nodes(
        service_names=[config.NEUTRON_OVS_SERVICE])
    os_faults_steps.terminate_service(config.NEUTRON_OVS_SERVICE, nodes=nodes)

    os_faults_steps.start_service(config.NEUTRON_OVS_SERVICE, nodes=nodes)

    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            server_2_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('ab973d26-55e0-478c-b5fd-35a3ea47e583')
def test_restart_many_times(
        neutron_2_servers_different_networks,
        nova_floating_ip,
        server_steps,
        os_faults_steps,
        agent_steps):
    """**Scenario:** Restart OVS-agents many times.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router
    #. Create server_1
    #. Create floating ip
    #. Create network_2 with subnet_2
    #. Add network_2 interface to router
    #. Create server_2 on another compute and connect it to network_2

    **Steps:**

    #. Attach floating IP to server_1
    #. Start ping from server_1 to server_2
    #. Restart ovs-agents
    #. Check that ping loss is not more than 2
    #. Repeat last 3 steps 40 times

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, router
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_fixed_ip=server_steps.get_fixed_ip(server_2)

    ovs_agents = agent_steps.get_agents(binary=config.NEUTRON_OVS_SERVICE)
    with server_steps.get_server_ssh(server_1) as server_ssh:
        for _ in range(40):
            with server_steps.check_ping_loss_context(
                    server_2_fixed_ip,
                    max_loss=config.NEUTRON_OVS_RESTART_MAX_PING_LOSS,
                    server_ssh=server_ssh):
                os_faults_steps.restart_services([config.NEUTRON_OVS_SERVICE])
                agent_steps.check_alive(
                    ovs_agents,
                    must_alive=True,
                    timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('6188b10f-c8f1-4d00-9c97-d163503592a5')
def test_restart_with_broadcast_traffic(
        neutron_2_servers_same_network,
        nova_floating_ip,
        server_steps,
        os_faults_steps,
        agent_steps):
    """**Scenario:** Restart OVS-agents with broadcast traffic on background.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create server_1
    #. Create floating ip
    #. Create server_2 on another compute and connect it to network

    **Steps:**

    #. Attach floating IP to server_1
    #. Start arping from server_1 to server_2
    #. Restart ovs-agents
    #. Check that ping loss is not more than 50

    **Teardown:**

    #. Delete servers
    #. Delete network, subnet, router
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_same_network.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_fixed_ip = server_steps.get_fixed_ip(server_2)

    ovs_agents = agent_steps.get_agents(binary=config.NEUTRON_OVS_SERVICE)
    with server_steps.get_server_ssh(server_1) as server_ssh:
        with server_steps.check_arping_loss_context(
                server_ssh,
                ip=server_2_fixed_ip,
                max_loss=config.NEUTRON_OVS_RESTART_MAX_ARPING_LOSS):
            os_faults_steps.restart_services([config.NEUTRON_OVS_SERVICE])
            agent_steps.check_alive(
                ovs_agents,
                timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('f92c6488-f87d-46d7-b2a5-13a98e10ab28')
def test_restart_adds_new_flows(
        server,
        os_faults_steps,
        agent_steps):
    """**Scenario:** Check that new flows are added after OVS-agents restart.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create server

    **Steps:**

    #. Get list of flows for br_int on server's compute
    #. Check that all cookies for flows is same
    #. Restart ovs-agents
    #. Get list of flows for br_int on server's compute
    #. Check that all cookies are changed

    **Teardown:**

    #. Delete servers
    #. Delete network, subnet, router
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    ovs_agents = agent_steps.get_agents(binary=config.NEUTRON_OVS_SERVICE)

    compute_host = getattr(server, config.SERVER_ATTR_HOST)
    compute_fqdn = os_faults_steps.get_fqdn_by_host_name(compute_host)
    compute_node = os_faults_steps.get_nodes(fqdns=[compute_fqdn])

    old_cookies = os_faults_steps.get_ovs_flows_cookies(compute_node)

    os_faults_steps.restart_services([config.NEUTRON_OVS_SERVICE])
    agent_steps.check_alive(ovs_agents,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    os_faults_steps.check_ovs_flow_cookies(compute_node,
                                           not_contain=old_cookies)


@pytest.mark.requires("vlan")
@pytest.mark.idempotent_id('51340e3b-5762-4bb5-b394-3f050263e96b')
def test_port_tags_immutable_after_restart(os_faults_steps):
    """Check that ports tags are the same after ovs-agents restart.

    **Steps:**

    #. Collect ovs-vsctl tags before restart
    #. Restart ovs-agents
    #. Collect ovs-vsctl tags after restart
    #. Check that values of the tag parameter for every port remain the same
    """
    before_restart_tags = os_faults_steps.get_ovs_vsctl_tags()
    os_faults_steps.restart_services([config.NEUTRON_OVS_SERVICE])
    os_faults_steps.check_ovs_vsctl_tags(expected_tags=before_restart_tags)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('f3935941-4262-41b3-bedb-d9777e63895f')
def test_restart_with_iperf_traffic(
        neutron_2_servers_iperf_different_networks,
        nova_floating_ip,
        server_steps,
        os_faults_steps,
        agent_steps):
    """**Scenario:** Restart OVS-agents with broadcast traffic on background.

    **Setup:**

    #. Create ubuntu image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create network_2 with subnet_2
    #. Create server_1
    #. Create server_2 on another compute and connect it to network
    #. Create floating ip

    **Steps:**

    #. Attach floating IP to server_1
    #. Start iperf traffic from server_1 to server_2, wait it done
    #. Check that iperf loss is 0
    #. Start iperf traffic from server_1 to server_2
    #. Restart ovs-agents
    #. Check that iperf loss is not more than 10%

    **Teardown:**

    #. Delete servers
    #. Delete network, subnet, router
    #. Delete floating IP
    #. Delete security group
    #. Delete ubuntu image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_iperf_different_networks.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_fixed_ip = server_steps.get_fixed_ip(server_2)

    ovs_agents = agent_steps.get_agents(binary=config.NEUTRON_OVS_SERVICE)
    with server_steps.get_server_ssh(server_1) as server_ssh:
        with server_steps.check_iperf_loss_context(
                server_ssh,
                ip=server_2_fixed_ip,
                port=config.IPERF_UDP_PORT,
                max_loss=0):
            pass
        with server_steps.check_iperf_loss_context(
                server_ssh,
                ip=server_2_fixed_ip,
                port=config.IPERF_UDP_PORT,
                max_loss=config.NEUTRON_OVS_RESTART_MAX_IPERF_LOSS):
            os_faults_steps.restart_services([config.NEUTRON_OVS_SERVICE])
            agent_steps.check_alive(
                ovs_agents,
                timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)


@pytest.mark.idempotent_id('10b85297-3511-4f96-bf39-16b7b14ab7c9')
@pytest.mark.parametrize(
    'neutron_2_servers_same_network', ['same_host'], indirect=True)
def test_restart_servers_on_single_compute(
        neutron_2_servers_same_network,
        nova_floating_ip,
        server_steps,
        os_faults_steps,
        agent_steps):
    """**Scenario:** Check connectivity for same host servers and one network.

    This test checks connectivity for instances scheduled on a single compute
    in a single private network during OVS-agents restating.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create server_1
    #. Create floating ip
    #. Create server_2 on same compute as server_1 and connect it to network

    **Steps:**

    #. Attach floating IP to server_1
    #. Start arping from server_1 to server_2
    #. Restart ovs-agents
    #. Check that ping loss is not more than 50

    **Teardown:**

    #. Delete servers
    #. Delete network, subnet, router
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_same_network.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_fixed_ip = server_steps.get_fixed_ip(server_2)

    ovs_agents = agent_steps.get_agents(binary=config.NEUTRON_OVS_SERVICE)
    with server_steps.get_server_ssh(server_1) as server_ssh:
        with server_steps.check_ping_loss_context(
                server_2_fixed_ip,
                max_loss=config.NEUTRON_OVS_RESTART_MAX_PING_LOSS,
                server_ssh=server_ssh):
            os_faults_steps.restart_services([config.NEUTRON_OVS_SERVICE])
            agent_steps.check_alive(
                ovs_agents, timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)


@pytest.mark.requires("computes_count >= 2 and vlan")
@pytest.mark.idempotent_id('28d8bd3d-160c-4c58-af46-edd7df2c4502')
@pytest.mark.parametrize('neutron_2_networks',
                         ['different_routers'],
                         indirect=True)
def test_no_connectivity_with_different_routers_during_restart(
        neutron_2_servers_different_networks,
        nova_floating_ip,
        server_steps,
        os_faults_steps,
        agent_steps):
    """**Scenario:** Check connectivity between networks on different routers.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create network_2 with subnet_2 and router_2
    #. Create server_1
    #. Create server_2 on another compute and connect it to network_2
    #. Create floating ip

    **Steps:**

    #. Attach floating IP to server_1
    #. Check that there is no ping between server_1 and server_2
    #. Restart ovs-agents
    #. Check that there is no ping between server_1 and server_2 during restart

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, routers
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_fixed_ip = server_steps.get_fixed_ip(server_2)

    ovs_agents = agent_steps.get_agents(binary=config.NEUTRON_OVS_SERVICE)
    with server_steps.get_server_ssh(server_1) as server_ssh:
        with server_steps.check_no_ping_context(
                server_2_fixed_ip,
                server_ssh=server_ssh):
            pass
        with server_steps.check_no_ping_context(
                server_2_fixed_ip,
                server_ssh=server_ssh):
            os_faults_steps.restart_services([config.NEUTRON_OVS_SERVICE])
            agent_steps.check_alive(
                ovs_agents,
                must_alive=True,
                timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
