"""
----------------------
Neutron l3 agent tests
----------------------
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


pytestmark = [pytest.mark.requires("not dvr and not l3_ha and vlan",
                                   "computes_count >= 2"),
              pytest.mark.destructive]


@pytest.mark.requires("l3_agent_nodes_count >= 3")
@pytest.mark.idempotent_id('e97bbed1-f1b2-4732-80f4-9b2919e846b2',
                           ban_count=1)
@pytest.mark.idempotent_id('aa00657f-765b-410d-a614-3a699622f818',
                           ban_count=2)
@pytest.mark.parametrize('ban_count', [1, 2])
@pytest.mark.parametrize('neutron_2_networks',
                         ['different_routers'],
                         indirect=True)
def test_ban_some_l3_agents(cirros_image,
                            flavor,
                            security_group,
                            neutron_2_servers_diff_nets_with_floating,
                            nova_create_floating_ip,
                            server_steps,
                            os_faults_steps,
                            agent_steps,
                            ban_count):
    """**Scenario:** Ban l3-agent and check that ping is available.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router1
    #. Create server_1
    #. Create network_2 with subnet_2
    #. Create server_2 on another compute and connect it to network_2
    #. Assign floating ips to servers

    **Steps:**

    #. Ping server_1 and server_2 from each other with floatings ip
    #. Get node with l3 agent for router_1
    #. Ban l3 agent for the node with pcs
    #. Wait for l3 agent becoming dead
    #. Check that router_1 was rescheduled
    #. Repeat last 4 steps if ban_count is 2
    #. Boot server_3 in network_1
    #. Associate floating ip for server_3
    #. Ping server_1 and server_3 from each other with internal ip
    #. Ping server_2 and server_1 from each other with floating ip
    #. Ping server_2 and server_3 from each other with floating ip

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, routers
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    network_1, network_2 = neutron_2_servers_diff_nets_with_floating.networks
    router_1, _ = neutron_2_servers_diff_nets_with_floating.routers
    servers = neutron_2_servers_diff_nets_with_floating.servers

    server_steps.check_ping_between_servers_via_floating(
        servers,
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    for _ in range(ban_count):
        old_l3_agent = agent_steps.get_l3_agents_for_router(router_1)[0]
        nodes_with_l3 = os_faults_steps.get_nodes_for_agents([old_l3_agent])

        os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE,
                                          nodes=nodes_with_l3)
        agent_steps.check_router_rescheduled(
            router_1,
            old_l3_agent,
            timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    server_3 = server_steps.create_servers(image=cirros_image,
                                           flavor=flavor,
                                           networks=[network_1],
                                           security_groups=[security_group],
                                           username=config.CIRROS_USERNAME,
                                           password=config.CIRROS_PASSWORD)[0]
    floating_ip = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_3, floating_ip)

    server_1, server_2 = neutron_2_servers_diff_nets_with_floating.servers
    ping_plan = {
        server_1: [(server_2, config.FLOATING_IP), (server_3,
                                                    config.FIXED_IP)],
        server_2: [(server_1, config.FLOATING_IP),
                   (server_3, config.FLOATING_IP)],
        server_3: [(server_2, config.FLOATING_IP), (server_1, config.FIXED_IP)]
    }
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("l3_agent_nodes_count >= 2")
@pytest.mark.idempotent_id('35c373ee-6aa5-4a44-8d89-4a627b8351ce',
                           agent_number=0)
@pytest.mark.idempotent_id('14369db2-b36c-47e8-8c52-0deac890a268',
                           agent_number=-1)
@pytest.mark.parametrize('agent_number',
                         [0, -1],
                         ids=['first', 'last'])
@pytest.mark.parametrize('neutron_2_networks',
                         ['different_routers'],
                         indirect=True)
def test_ban_all_l3_agents_restart_one(
        cirros_image,
        flavor,
        security_group,
        neutron_2_servers_diff_nets_with_floating,
        nova_create_floating_ip,
        server_steps,
        os_faults_steps,
        agent_steps,
        agent_number):
    """**Scenario:** Ban all l3-agent agents and restart one.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create server_1
    #. Create network_2 with subnet_2
    #. Create server_2 on another compute and connect it to network_2
    #. Assign floating ips to servers

    **Steps:**

    #. Check that ping from server_1 to server_2 with floating ips
        and 8.8.8.8 is successful
    #. Check that there is no ping between server_1 and server_2 via
        internal ips.
    #. Get node with l3 agent for router_1
    #. Ban l3 agent for the node with pcs
    #. Wait for l3 agent becoming dead
    #. Check that router_1 was rescheduled
    #. Repeat last 3 steps for all l3 agents except for one
    #. Ban the remaining l3 agent
    #. Wait for l3 agent becoming dead if agent_number is not 0
    #. Clear the first/last banned l3 agent
    #. Wait for l3 agent becoming active
    #. Boot server_3 in network_1
    #. Associate floating ip for server_3
    #. Ping server_1 and server_3 from each other with both ips
    #. Ping server_2 and server_3 from each other with floating ip
    #. Check that ping from server_1 to 8.8.8.8 is successful
    #. Check that ping from server_3 to 8.8.8.8 is successful

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, routers
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    network_1, network_2 = neutron_2_servers_diff_nets_with_floating.networks
    server_1, server_2 = neutron_2_servers_diff_nets_with_floating.servers
    router_1, _ = neutron_2_servers_diff_nets_with_floating.routers
    server_2_fixed_ip = server_steps.get_fixed_ip(server_2)
    server_2_floating_ip = server_steps.get_floating_ip(server_2,
                                                        config.FLOATING_IP)

    with server_steps.get_server_ssh(server_1) as server_ssh:
        for ip_to_ping in (config.GOOGLE_DNS_IP, server_2_floating_ip):
            server_steps.check_ping_for_ip(ip_to_ping,
                                           server_ssh,
                                           timeout=config.PING_CALL_TIMEOUT)
        with server_steps.check_no_ping_context(
                server_2_fixed_ip,
                server_ssh=server_ssh):
            pass

    banned_agents = []
    l3_agents_count = len(
        agent_steps.get_agents(binary=config.NEUTRON_L3_SERVICE))

    for number in range(l3_agents_count - 1):
        l3_agent = agent_steps.get_l3_agents_for_router(router_1)[0]
        nodes_with_l3 = os_faults_steps.get_nodes_for_agents([l3_agent])
        os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE,
                                          nodes=nodes_with_l3)
        agent_steps.check_alive([l3_agent],
                                must_alive=False,
                                timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
        agent_steps.check_router_rescheduled(
            router_1,
            l3_agent,
            timeout=config.AGENT_RESCHEDULING_TIMEOUT)
        banned_agents.append(l3_agent)

    l3_agent = agent_steps.get_l3_agents_for_router(router_1)[0]
    nodes_with_l3 = os_faults_steps.get_nodes_for_agents([l3_agent])
    os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE,
                                      nodes=nodes_with_l3)
    # there are no active agents after we have banned the last
    if agent_number != 0:
        # we should check it only if we want to clear
        # the last banned agent later
        agent_steps.check_alive(
            [l3_agent],
            must_alive=False,
            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    banned_agents.append(l3_agent)

    agent_to_clear = banned_agents[agent_number]
    nodes_with_l3 = os_faults_steps.get_nodes_for_agents([agent_to_clear])
    os_faults_steps.start_service(config.NEUTRON_L3_SERVICE,
                                  nodes=nodes_with_l3)
    agent_steps.check_alive([agent_to_clear],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    server_3 = server_steps.create_servers(image=cirros_image,
                                           flavor=flavor,
                                           networks=[network_1],
                                           security_groups=[security_group],
                                           username=config.CIRROS_USERNAME,
                                           password=config.CIRROS_PASSWORD)[0]
    floating_ip = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_3, floating_ip)

    ping_plan = {
        server_1: [config.GOOGLE_DNS_IP, (server_2, config.FLOATING_IP),
                   server_3],
        server_2: [(server_1, config.FLOATING_IP),
                   (server_3, config.FLOATING_IP)],
        server_3: [config.GOOGLE_DNS_IP, (server_2, config.FLOATING_IP),
                   server_1]
    }
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("l3_agent_nodes_count >= 1")
@pytest.mark.idempotent_id('e4338068-7a16-4db9-9645-68b074c91f91')
@pytest.mark.parametrize('neutron_2_networks',
                         ['different_routers'],
                         indirect=True)
def test_ban_l3_agent_many_times(cirros_image,
                                 flavor,
                                 security_group,
                                 neutron_2_servers_diff_nets_with_floating,
                                 nova_create_floating_ip,
                                 server_steps,
                                 os_faults_steps,
                                 agent_steps):
    """**Scenario:** Ban l3-agent many times.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create server_1
    #. Create network_2 with subnet_2
    #. Create server_2 on another compute and connect it to network_2
    #. Assign floating ips to servers

    **Steps:**

    #. Ping server_1 and server_2 from each other with floatings ip
    #. Ban all l3 agents except for one
    #. Ban active l3 agent
    #. Wait for l3 agent becoming dead
    #. Clear l3 agent from the previous step
    #. Wait for l3 agent becoming active
    #. Repeat last 4 steps 40 times
    #. Boot server_3 in network_1
    #. Associate floating ip for server_3
    #. Ping server_1 and server_3 from each other with both ips
    #. Ping server_2 and server_3 from each other with floating ip
    #. Check that ping from server_1 to 8.8.8.8 is successful
    #. Check that ping from server_3 to 8.8.8.8 is successful

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, routers
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    network_1, network_2 = neutron_2_servers_diff_nets_with_floating.networks
    servers = neutron_2_servers_diff_nets_with_floating.servers

    server_steps.check_ping_between_servers_via_floating(
        servers,
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    l3_agents = agent_steps.get_agents(binary=config.NEUTRON_L3_SERVICE)
    l3_agent = l3_agents[0]
    if len(l3_agents) > 1:
        for agent_to_ban in l3_agents[1:]:
            nodes_with_l3 = os_faults_steps.get_nodes_for_agents(
                [agent_to_ban])
            os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE,
                                              nodes=nodes_with_l3)
            agent_steps.check_alive([agent_to_ban],
                                    must_alive=False,
                                    timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    for _ in range(40):
        nodes_with_l3 = os_faults_steps.get_nodes_for_agents([l3_agent])
        os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE,
                                          nodes=nodes_with_l3)
        agent_steps.check_alive([l3_agent],
                                must_alive=False,
                                timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

        os_faults_steps.start_service(config.NEUTRON_L3_SERVICE,
                                      nodes=nodes_with_l3)
        agent_steps.check_alive([l3_agent],
                                timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    server_3 = server_steps.create_servers(image=cirros_image,
                                           flavor=flavor,
                                           networks=[network_1],
                                           security_groups=[security_group],
                                           username=config.CIRROS_USERNAME,
                                           password=config.CIRROS_PASSWORD)[0]
    floating_ip = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_3, floating_ip)

    server_1, server_2 = neutron_2_servers_diff_nets_with_floating.servers
    ping_plan = {
        server_1: [config.GOOGLE_DNS_IP, (server_2, config.FLOATING_IP),
                   server_3],
        server_2: [(server_1, config.FLOATING_IP),
                   (server_3, config.FLOATING_IP)],
        server_3: [config.GOOGLE_DNS_IP, (server_2, config.FLOATING_IP),
                   server_1]
    }
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("l3_agent_nodes_count >= 1")
@pytest.mark.idempotent_id('11660a80-2510-419d-a9eb-471e4ff7e20c')
@pytest.mark.parametrize('neutron_2_networks',
                         ['different_routers'],
                         indirect=True)
def test_kill_l3_agent_process(cirros_image,
                               flavor,
                               security_group,
                               neutron_2_servers_diff_nets_with_floating,
                               nova_create_floating_ip,
                               server_steps,
                               os_faults_steps,
                               agent_steps):
    """**Scenario:** Kill l3-agent process and check that ping is available.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router1
    #. Create server_1
    #. Create network_2 with subnet_2
    #. Create server_2 on another compute and connect it to network_2
    #. Assign floating ips to servers

    **Steps:**

    #. Ping server_1 and server_2 from each other with floatings ip
    #. Get node with l3 agent for router_1
    #. Get PID of l3 agent process
    #. Send SIGKILL to the process
    #. Wait for l3 agent becoming active
    #. Boot server_3 in network_1
    #. Associate floating ip for server_3
    #. Ping server_1 and server_3 from each other with internal ip
    #. Ping server_2 and server_1 from each other with floating ip
    #. Ping server_2 and server_3 from each other with floating ip

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, routers
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    network_1, network_2 = neutron_2_servers_diff_nets_with_floating.networks
    router_1, _ = neutron_2_servers_diff_nets_with_floating.routers
    server_1, server_2 = neutron_2_servers_diff_nets_with_floating.servers

    server_steps.check_ping_between_servers_via_floating(
        (server_1, server_2),
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    l3_agent = agent_steps.get_l3_agents_for_router(router_1)[0]
    nodes_with_l3 = os_faults_steps.get_nodes_for_agents([l3_agent])

    pid = os_faults_steps.get_process_pid(nodes_with_l3,
                                          config.NEUTRON_L3_SERVICE)
    os_faults_steps.send_signal_to_process(nodes_with_l3,
                                           pid=pid,
                                           signal=signal.SIGKILL)
    agent_steps.check_alive([l3_agent],
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    server_3 = server_steps.create_servers(image=cirros_image,
                                           flavor=flavor,
                                           networks=[network_1],
                                           security_groups=[security_group],
                                           username=config.CIRROS_USERNAME,
                                           password=config.CIRROS_PASSWORD)[0]
    floating_ip = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_3, floating_ip)

    ping_plan = {
        server_1: [(server_2, config.FLOATING_IP), (server_3,
                                                    config.FIXED_IP)],
        server_2: [(server_1, config.FLOATING_IP),
                   (server_3, config.FLOATING_IP)],
        server_3: [(server_2, config.FLOATING_IP), (server_1, config.FIXED_IP)]
    }
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("l3_agent_nodes_count >= 1")
@pytest.mark.idempotent_id('6d7ae90c-d6a1-4c90-b0d3-70a1fd4bafd7')
@pytest.mark.parametrize('neutron_2_networks',
                         ['different_routers'],
                         indirect=True)
def test_l3_agent_after_drop_rabbit_port(
        neutron_2_servers_diff_nets_with_floating,
        server_steps,
        os_faults_steps,
        agent_steps):
    """**Scenario:** Drop rabbit port and check l3-agent work.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create server_1
    #. Create network_2 with subnet_2
    #. Create server_2 on another compute and connect it to network_2
    #. Assign floating ips to servers

    **Steps:**

    #. Ping server_1 and server_2 from each other with floatings ip
    #. Get node with l3 agent for router_1
    #. Drop rabbit's port 5673 using iptables
    #. Wait for l3 agent becoming dead
    #. Check that router_1 was rescheduled
    #. Ping server_1 and server_2 from each other with floatings ip
    #. Remove rule for dropping port using iptables
    #. Wait for l3 agent becoming active

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, routers
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    router_1, _ = neutron_2_servers_diff_nets_with_floating.routers
    servers = neutron_2_servers_diff_nets_with_floating.servers

    server_steps.check_ping_between_servers_via_floating(
        servers,
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    all_l3_agents = agent_steps.get_agents(binary=config.NEUTRON_L3_SERVICE)

    l3_agent = agent_steps.get_l3_agents_for_router(router_1)[0]
    nodes_with_l3 = os_faults_steps.get_nodes_for_agents([l3_agent])
    os_faults_steps.add_rule_to_drop_port(nodes_with_l3, config.RABBIT_PORT)
    agent_steps.check_alive([l3_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)
    agent_steps.check_router_rescheduled(
        router_1,
        l3_agent,
        timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    server_steps.check_ping_between_servers_via_floating(
        servers,
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    os_faults_steps.remove_rule_to_drop_port(nodes_with_l3, config.RABBIT_PORT)
    agent_steps.check_alive(all_l3_agents,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)


@pytest.mark.requires("l3_agent_nodes_count >= 2")
@pytest.mark.idempotent_id('772bf185-77be-49dc-89fd-40195b66fe42',
                           controller_cmd=config.FUEL_PRIMARY_CONTROLLER_CMD)
@pytest.mark.idempotent_id(
    'a65e56a3-c1b7-41dd-86ee-bd062fe8b328',
    controller_cmd=config.FUEL_NON_PRIMARY_CONTROLLERS_CMD)
@pytest.mark.parametrize('controller_cmd',
                         [config.FUEL_PRIMARY_CONTROLLER_CMD,
                          config.FUEL_NON_PRIMARY_CONTROLLERS_CMD],
                         ids=['primary', 'non_primary'])
@pytest.mark.parametrize('neutron_2_networks',
                         ['different_routers'],
                         indirect=True)
def test_check_l3_agent_after_destroy_controller(
        cirros_image,
        flavor,
        security_group,
        neutron_2_servers_diff_nets_with_floating,
        nova_create_floating_ip,
        os_faults_steps,
        agent_steps,
        router_steps,
        server_steps,
        controller_cmd):
    """**Scenario:** Destroy controller and check L3 agent is alive.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create server_1
    #. Create network_2 with subnet_2
    #. Create server_2 on another compute and connect it to network_2
    #. Assign floating ips to servers

    **Steps:**

    #. Get primary/non-primary controller
    #. Get L3 agent for primary/non-primary controller node
    #. Reschedule router_1 to L3 agent on primary/non-primary
        controller if it is not there yet
    #. Ping server_1 and server_2 from each other with floatings ip
    #. Check that ping from server_1 and server_2 to 8.8.8.8 is successful
    #. Destroy primary/non-primary controller
    #. Wait for L3 agent becoming dead
    #. Check that all routers rescheduled from primary/non-primary controller
    #. Boot server_3 in network_1
    #. Associate floating ip for server_3
    #. Ping server_1 and server_3 from each other with both ips
    #. Ping server_2 and server_3 from each other with floating ip
    #. Check that ping from server_1 to 8.8.8.8 is successful
    #. Check that ping from server_3 to 8.8.8.8 is successful

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, routers
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    network_1, _ = neutron_2_servers_diff_nets_with_floating.networks
    router_1, router_2 = neutron_2_servers_diff_nets_with_floating.routers
    server_1, server_2 = neutron_2_servers_diff_nets_with_floating.servers

    controller = os_faults_steps.get_node_by_cmd(controller_cmd)
    l3_agent = agent_steps.get_agents(node=controller,
                                      binary=config.NEUTRON_L3_SERVICE)[0]
    agent_steps.reschedule_router_to_l3_agent(
        l3_agent, router_1, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    ping_plan = {
        server_1: [config.GOOGLE_DNS_IP, (server_2, config.FLOATING_IP)],
        server_2: [config.GOOGLE_DNS_IP, (server_1, config.FLOATING_IP)]
    }
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    os_faults_steps.poweroff_nodes(controller)
    agent_steps.check_alive([l3_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    for router in (router_1, router_2):
        agent_steps.check_router_rescheduled(
            router, l3_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    router_steps.check_routers_count_for_agent(l3_agent, expected_count=0)

    server_3 = server_steps.create_servers(image=cirros_image,
                                           flavor=flavor,
                                           networks=[network_1],
                                           security_groups=[security_group],
                                           username=config.CIRROS_USERNAME,
                                           password=config.CIRROS_PASSWORD)[0]
    floating_ip = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_3, floating_ip)

    ping_plan = {
        server_1: [(server_2, config.FLOATING_IP), (server_3,
                                                    config.FIXED_IP)],
        server_2: [(server_1, config.FLOATING_IP),
                   (server_3, config.FLOATING_IP)],
        server_3: [(server_2, config.FLOATING_IP), (server_1, config.FIXED_IP)]
    }
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("l3_agent_nodes_count >= 2")
@pytest.mark.idempotent_id('bc45b59d-1870-4b62-b8c6-d4247cf7bbf1')
@pytest.mark.parametrize('neutron_2_networks',
                         ['different_routers'],
                         indirect=True)
def test_check_l3_agent_after_reset_primary_controller(
        cirros_image,
        flavor,
        security_group,
        neutron_2_servers_diff_nets_with_floating,
        nova_create_floating_ip,
        os_faults_steps,
        agent_steps,
        router_steps,
        server_steps):
    """**Scenario:** Reset controller and check L3 agent is alive.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create server_1
    #. Create network_2 with subnet_2
    #. Create server_2 on another compute and connect it to network_2
    #. Assign floating ips to servers

    **Steps:**

    #. Get primary controller
    #. Get L3 agent for primary controller node
    #. Reschedule router_1 to L3 agent on primary controller
        if it is not there yet
    #. Ping server_1 and server_2 from each other with floatings ip
    #. Check that ping from server_1 and server_2 to 8.8.8.8 is successful
    #. Reset or reboot primary controller
    #. Wait for L3 agent becoming dead
    #. Check that all routers rescheduled from primary controller
    #. Boot server_3 in network_1
    #. Associate floating ip for server_3
    #. Ping server_1 and server_3 from each other with both ips
    #. Ping server_2 and server_3 from each other with floating ip
    #. Check that ping from server_1 to 8.8.8.8 is successful
    #. Check that ping from server_3 to 8.8.8.8 is successful

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, routers
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    network_1, _ = neutron_2_servers_diff_nets_with_floating.networks
    router_1, router_2 = neutron_2_servers_diff_nets_with_floating.routers
    server_1, server_2 = neutron_2_servers_diff_nets_with_floating.servers

    controller = os_faults_steps.get_node_by_cmd(
        config.FUEL_PRIMARY_CONTROLLER_CMD)
    l3_agent = agent_steps.get_agents(node=controller,
                                      binary=config.NEUTRON_L3_SERVICE)[0]
    agent_steps.reschedule_router_to_l3_agent(
        l3_agent, router_1, timeout=config.AGENT_RESCHEDULING_TIMEOUT)

    ping_plan = {
        server_1: [config.GOOGLE_DNS_IP, (server_2, config.FLOATING_IP)],
        server_2: [config.GOOGLE_DNS_IP, (server_1, config.FLOATING_IP)]
    }
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    os_faults_steps.reset_nodes(controller)
    agent_steps.check_alive([l3_agent],
                            must_alive=False,
                            timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    for router in (router_1, router_2):
        agent_steps.check_router_rescheduled(
            router, l3_agent, timeout=config.AGENT_RESCHEDULING_TIMEOUT)
    router_steps.check_routers_count_for_agent(l3_agent, expected_count=0)

    server_3 = server_steps.create_servers(image=cirros_image,
                                           flavor=flavor,
                                           networks=[network_1],
                                           security_groups=[security_group],
                                           username=config.CIRROS_USERNAME,
                                           password=config.CIRROS_PASSWORD)[0]
    floating_ip = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_3, floating_ip)

    ping_plan = {
        server_1: [(server_2, config.FLOATING_IP), (server_3,
                                                    config.FIXED_IP)],
        server_2: [(server_1, config.FLOATING_IP),
                   (server_3, config.FLOATING_IP)],
        server_3: [(server_2, config.FLOATING_IP), (server_1, config.FIXED_IP)]
    }
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
