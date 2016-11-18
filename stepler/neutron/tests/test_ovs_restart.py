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

pytestmark = pytest.mark.requires("computes_count_gte(2)")


@pytest.mark.idempotent_id('ee080cc2-b658-42cf-ac0b-f5eab906fcf5')
def test_restart_with_pcs_disable_enable(
        ovs_restart_resources,
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
    server_1, server_2 = ovs_restart_resources.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_fixed_ip = next(iter(server_steps.get_ips(server_2,
                                                       config.FIXED_IP)))

    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            server_2_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    os_faults_steps.restart_services([config.NEUTRON_OVS_SERVICE])

    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            server_2_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.idempotent_id('310c630d-38f0-402b-9423-ffb14fb766b2')
def test_restart_with_pcs_ban_clear(
        ovs_restart_resources,
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
    server_1, server_2 = ovs_restart_resources.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_fixed_ip = next(iter(server_steps.get_ips(server_2,
                                                       config.FIXED_IP)))

    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            server_2_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    os_faults_steps.terminate_services([config.NEUTRON_OVS_SERVICE])
    os_faults_steps.start_services([config.NEUTRON_OVS_SERVICE])

    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            server_2_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
