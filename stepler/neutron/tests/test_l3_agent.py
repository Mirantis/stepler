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
                                  "computes_count_gte(2)")


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
                          neutron_2_servers_different_networks,
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

    **Steps:**

    #. Assign floating ips to servers
    #. Ping server_1 and server_2 from each other with floatings ip
    #. Get node with l3 agent for router_1
    #. Ban l3 agent for the node with pcs
    #. Wait for l3 agent becoming dead
    #. Check that router1 was rescheduled
    #. Repeat last 4 steps if ban_count is 2
    #. Boot server_3 in network_1
    #. Associate floating ip for server_3
    #. Ping server_1 and server_2 from each other with internal ip
    #. Ping server_2 and server_1 from each other with floating ip
    #. Ping server_2 and server_3 from each other with floating ip

    **Teardown:**

    #. Delete servers
    #. Delete networks, subnets, routers
    #. Delete floating IP
    #. Delete security group
    #. Delete cirros image
    #. Delete flavor
    """
    network_1, network_2 = neutron_2_servers_different_networks.networks
    router_1 = neutron_2_servers_different_networks.router
    servers = neutron_2_servers_different_networks.servers

    for server in servers:
        floating_ip = nova_create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)

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

    server_1, server_2 = neutron_2_servers_different_networks.servers
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
