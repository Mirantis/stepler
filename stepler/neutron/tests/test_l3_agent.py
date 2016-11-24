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

import pytest

from stepler import config

# TODO(agromov): add destructive marker after os-faults release
pytestmark = pytest.mark.requires("l3_agent_nodes_count >= 3",
                                  "computes_count >= 2")


@pytest.mark.idempotent_id('e97bbed1-f1b2-4732-80f4-9b2919e846b2',
                           ban_count=1)
@pytest.mark.idempotent_id('aa00657f-765b-410d-a614-3a699622f818',
                           ban_count=2)
@pytest.mark.parametrize('ban_count', [1, 2])
@pytest.mark.parametrize('neutron_2_networks',
                         ['different_routers'],
                         indirect=True)
def test_ban_one_l3_agent(cirros_image,
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
    #. Check that router1 was rescheduled
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
        nodes_with_l3 = os_faults_steps.get_nodes_for_l3_agents([old_l3_agent])

        os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE,
                                          nodes=nodes_with_l3)
        agent_steps.check_router_rescheduled(
            router_1,
            old_l3_agent,
            timeout=config.L3_AGENT_RESCHEDULING_TIMEOUT)

    server_3 = server_steps.create_servers(image=cirros_image,
                                           flavor=flavor,
                                           networks=[network_1],
                                           security_groups=[security_group],
                                           username=config.CIRROS_USERNAME,
                                           password=config.CIRROS_PASSWORD)[0]
    floating_ip = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_3, floating_ip)

    server_1, server_2 = neutron_2_servers_diff_nets_with_floating.servers
    server_steps.check_ping_between_servers_via_floating(
        (server_1, server_3,),
        ip_types=(config.FIXED_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
    server_steps.check_ping_between_servers_via_floating(
        (server_1, server_2,),
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
    server_steps.check_ping_between_servers_via_floating(
        (server_2, server_3,),
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


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
            nodes_with_l3 = os_faults_steps.get_nodes_for_l3_agents(
                [agent_to_ban])
            os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE,
                                              nodes=nodes_with_l3)
            agent_steps.check_alive([agent_to_ban],
                                    must_alive=False,
                                    timeout=config.NEUTRON_AGENT_ALIVE_TIMEOUT)

    for _ in range(40):
        nodes_with_l3 = os_faults_steps.get_nodes_for_l3_agents([l3_agent])
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

    server_steps.check_ping_between_servers_via_floating(
        (server_1, server_3,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
    server_steps.check_ping_between_servers_via_floating(
        (server_2, server_3,),
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    for server in (server_1, server_3,):
        with server_steps.get_server_ssh(server) as server_ssh:
            server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP,
                                           server_ssh,
                                           timeout=config.PING_CALL_TIMEOUT)
