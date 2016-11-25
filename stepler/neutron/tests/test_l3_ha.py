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
    #. Check that ping loss is not more than 10 * ``ban_count`` packets.

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
                agents = agent_steps.get_l3_agents_for_router(
                    router_1, filter_attrs=config.HA_STATE_ACTIVE_ATTRS)
                agent_node = os_faults_steps.get_nodes_for_l3_agents(agents[:
                                                                            1])
                os_faults_steps.terminate_service(
                    config.NEUTRON_L3_SERVICE, nodes=agent_node)
                agent_steps.check_l3_ha_router_rescheduled(
                    router_1,
                    old_l3_agent=agents[0],
                    timeout=config.L3_AGENT_RESCHEDULING_TIMEOUT)
