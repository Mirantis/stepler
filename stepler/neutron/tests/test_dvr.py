"""
-----------------
Neutron DVR tests
-----------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from stepler import config


@pytest.mark.requires("computes_count_gte(2)")
@pytest.mark.idempotent_id('91853195-c456-464c-b0a4-5655acee7769')
@pytest.mark.parametrize('router', [dict(distributed=True)], indirect=True)
@pytest.mark.parametrize('neutron_2_servers_different_networks',
                         ['same_host', 'different_hosts'],
                         indirect=True)
def test_check_east_west_connectivity_between_instances(
        neutron_2_servers_different_networks,
        nova_floating_ip,
        server_steps):
    """**Scenario:** Check east-west connectivity between instances.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and DVR
    #. Create server_1
    #. Create network_2 with subnet_2
    #. Add network_2 interface to router
    #. Create server_2 and connect it to network_2

    **Steps:**

    #. Assign floating ip to server_1
    #. Check that ping from server_1 to server_2 is successful

    **Teardown:**

    #. Delete servers
    #. Delete cirros image
    #. Delete security group
    #. Delete flavor
    #. Delete router
    #. Delete subnets
    #. Delete networks
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_ip = next(iter(server_steps.get_ips(server_2, config.FIXED_IP)))
    with server_steps.get_server_ssh(server_1) as server_1_ssh:
        server_steps.check_ping_for_ip(
            server_2_ip,
            server_1_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("computes_count_gte(2)")
@pytest.mark.idempotent_id('f3848003-ff36-4f87-899d-de6d3a321b65')
@pytest.mark.parametrize('router', [dict(distributed=True)], indirect=True)
def test_check_connectivity_to_north_south_routing(cirros_image,
                                                   flavor,
                                                   security_group,
                                                   net_subnet_router,
                                                   server,
                                                   nova_floating_ip,
                                                   server_steps):
    """**Scenario:** Check connectivity to North-South-Routing.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and DVR
    #. Add network interface to router
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Check that ping from server to 8.8.8.8 is successful

    **Teardown:**

    #. Delete server
    #. Delete cirros image
    #. Delete security group
    #. Delete flavor
    #. Delete router
    #. Delete subnet
    #. Delete network
    """
    server_steps.attach_floating_ip(server, nova_floating_ip)

    with server_steps.get_server_ssh(server) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh,
            timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.idempotent_id('bbc32bc5-d3ed-4e25-a957-04288420dc54')
@pytest.mark.parametrize('router', [dict(distributed=True)], indirect=True)
def test_north_south_connectivity_after_ban_clear_l3_on_compute(
        cirros_image,
        flavor,
        security_group,
        net_subnet_router,
        server,
        nova_floating_ip,
        os_faults_steps,
        server_steps):
    """**Scenario:** Check North-South connectivity after ban/clear l3 agent.

    This test checks connectivity to North-South-Routing after ban and clear
        L3 agent on compute.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and DVR
    #. Add network interface to router
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Check that ping from server to 8.8.8.8 is successful
    #. Terminate L3 service on compute with server
    #. Start L3 service on compute with server
    #. Check that ping from server to 8.8.8.8 is successful

    **Teardown:**

    #. Delete server
    #. Delete cirros image
    #. Delete security group
    #. Delete flavor
    #. Delete router
    #. Delete subnet
    #. Delete network
    """
    server_steps.attach_floating_ip(server, nova_floating_ip)

    with server_steps.get_server_ssh(server) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh,
            timeout=config.PING_CALL_TIMEOUT)

    compute_node = os_faults_steps.get_node(
        fqdns=[getattr(server, config.SERVER_HOST_ATTR)])
    os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE, compute_node)
    os_faults_steps.start_service(config.NEUTRON_L3_SERVICE, compute_node)

    with server_steps.get_server_ssh(server) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh,
            timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.idempotent_id('db7e0ff4-d76c-469e-82a1-478c1c0b9a8f')
@pytest.mark.parametrize('router', [dict(distributed=True)], indirect=True)
@pytest.mark.parametrize('neutron_2_servers_different_networks',
                         ['different_hosts'], indirect=True)
def test_east_west_connectivity_after_ban_clear_l3_on_compute(
        neutron_2_servers_different_networks,
        nova_floating_ip,
        get_ssh_proxy_cmd,
        os_faults_steps,
        server_steps):
    """**Scenario:** Check east-west connectivity after ban/clear l3 agent.

    This test checks east-west connectivity between instances on different
        computes after ban and clear l3 agent on one of them.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and DVR
    #. Create server_1
    #. Create network_2 with subnet_2
    #. Add network_2 interface to router
    #. Create server_2 and connect it to network_2

    **Steps:**

    #. Terminate l3-service on the compute with server_1
    #. Start l3-service on the compute with server_1
    #. Check that ping from server_1 to server_2 by internal ip is successful

    **Teardown:**

    #. Delete servers
    #. Delete cirros image
    #. Delete security group
    #. Delete flavor
    #. Delete router
    #. Delete subnets
    #. Delete networks
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers

    server_1_host = os_faults_steps.get_node(
        fqdns=[getattr(server_1, config.SERVER_HOST_ATTR)])
    os_faults_steps.terminate_service(config.NEUTRON_L3_SERVICE, server_1_host)
    os_faults_steps.start_service(config.NEUTRON_L3_SERVICE, server_1_host)

    proxy_cmd = get_ssh_proxy_cmd(server_1)
    server_2_ip = next(iter(server_steps.get_ips(server_2, config.FIXED_IP)))
    with server_steps.get_server_ssh(
            server_1, proxy_cmd=proxy_cmd) as server_1_ssh:
        server_steps.check_ping_for_ip(
            server_2_ip,
            server_1_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
