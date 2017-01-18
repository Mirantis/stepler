"""
--------------------------
Neutron connectivity tests
--------------------------
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


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id(
    '645e141b-f233-4872-a4b0-6762c07c3d7c',
    neutron_2_servers_same_network='same_host')
@pytest.mark.idempotent_id(
    '318367e5-63c5-415a-897e-50afb20657d7',
    neutron_2_servers_same_network='different_hosts')
@pytest.mark.parametrize('neutron_2_servers_same_network',
                         ['same_host', 'different_hosts'],
                         indirect=True)
def test_connectivity_between_servers_same_network(
        neutron_2_servers_same_network,
        get_ssh_proxy_cmd,
        server_steps):
    """**Scenario:** Check connectivity between servers on the same network.

    This test checks connectivity by internal IP between servers on the same
    network and hosted on the same or different compute nodes.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create server_1
    #. Create server_2 on the same or another compute

    **Steps:**

    #. Ping server_2 from server_1
    #. Ping server_1 from server_2

    **Teardown:**

    #. Delete servers
    #. Delete router, subnet and network
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_1, server_2 = neutron_2_servers_same_network.servers

    for server_init, server_dest in ((server_1, server_2),
                                     (server_2, server_1)):
        proxy_cmd = get_ssh_proxy_cmd(server_init)
        server_dest_ip = server_steps.get_fixed_ip(server_init)
        with server_steps.get_server_ssh(
                server_init, proxy_cmd=proxy_cmd) as server_init_ssh:
            server_steps.check_ping_for_ip(
                server_dest_ip,
                server_init_ssh,
                timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id(
    '372a9712-1f14-47c4-9878-9a5412206639',
    neutron_2_servers_different_networks='same_host')
@pytest.mark.idempotent_id(
    'a3382ca0-03f2-4a07-afb9-6f1fcd69a9d3',
    neutron_2_servers_different_networks='different_hosts')
@pytest.mark.parametrize('neutron_2_servers_different_networks',
                         ['same_host', 'different_hosts'],
                         indirect=True)
def test_connectivity_between_servers_diff_networks(
        neutron_2_servers_different_networks,
        get_ssh_proxy_cmd,
        server_steps):
    """**Scenario:** Check connectivity between servers on different networks.

    This test checks connectivity by internal IP between servers on different
    networks and hosted on the same or different compute nodes.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router
    #. Create network_2 with subnet_2
    #. Add network_2 interface to router
    #. Create server_1 connected to network_1
    #. Create server_2 connected to network_2 on the same or another compute

    **Steps:**

    #. Ping server_2 from server_1
    #. Ping server_1 from server_2

    **Teardown:**

    #. Delete servers
    #. Delete router
    #  Delete subnet_1 and network_1
    #  Delete subnet_2 and network_2
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers

    for server_init, server_dest in ((server_1, server_2),
                                     (server_2, server_1)):
        proxy_cmd = get_ssh_proxy_cmd(server_init)
        server_dest_ip = server_steps.get_fixed_ip(server_init)
        with server_steps.get_server_ssh(
                server_init, proxy_cmd=proxy_cmd) as server_init_ssh:
            server_steps.check_ping_for_ip(
                server_dest_ip,
                server_init_ssh,
                timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id(
    '4327a3db-a65a-4047-9eca-a44188dd2783',
    neutron_2_servers_different_networks='same_host')
@pytest.mark.idempotent_id(
    'aef27c07-5015-4220-8bcc-a66d7e324c6c',
    neutron_2_servers_different_networks='different_hosts')
@pytest.mark.parametrize('neutron_2_servers_different_networks',
                         ['same_host', 'different_hosts'],
                         indirect=True)
def test_connectivity_floating_between_servers(
        neutron_2_servers_different_networks,
        nova_create_floating_ip,
        server_steps):
    """**Scenario:** Check connectivity by floating IP between servers.

    This test checks connectivity by floating IP between servers on different
    networks and hosted on the same or different compute nodes.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1
    #. Create network_2 with subnet_2
    #. Create router and add interfaces to both subnets
    #. Create server_1 connected to network_1
    #. Create server_2 connected to network_2 on the same or another compute

    **Steps:**

    #. Assign floating ip to server_1
    #. Assign floating ip to server_2
    #. Ping server_2 from server_1
    #. Ping server_1 from server_2

    **Teardown:**

    #. Delete servers
    #. Delete router
    #  Delete subnet_1 and network_1
    #  Delete subnet_2 and network_2
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_1, server_2 = neutron_2_servers_different_networks.servers

    floating_ip_1 = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_1, floating_ip_1)

    floating_ip_2 = nova_create_floating_ip()
    server_steps.attach_floating_ip(server_2, floating_ip_2)

    server_steps.check_ping_between_servers_via_floating(
        [server_1, server_2],
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.idempotent_id('1b6a3348-0bfe-4233-a12f-4d8246fb470a')
def test_connectivity_external(
        server,
        get_ssh_proxy_cmd,
        server_steps):
    """**Scenario:** Check connectivity to external IP with external router.

    This test checks connectivity to external resource from server with router
    to external network.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet
    #. Create router, add gateway and interface to subnet
    #. Create server

    **Steps:**

    #. Ping 8.8.8.8 from server

    **Teardown:**

    #. Delete server
    #. Delete router
    #. Delete subnet and network
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    proxy_cmd = get_ssh_proxy_cmd(server)

    with server_steps.get_server_ssh(
            server, proxy_cmd=proxy_cmd) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP, server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.idempotent_id('645e141b-f233-4872-a4b0-6762c07c3d7c')
def test_connectivity_between_servers_diff_subnets(
        neutron_2_servers_different_subnets,
        get_ssh_proxy_cmd,
        server_steps):
    """**Scenario:** Check connectivity between servers on different subnets.

    This test checks connectivity by internal IP between servers on different
    subnets of the same network and hosted on the same compute node.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet_1 and router
    #. Create server_1
    #. Create subnet_2 and add router interface
    #. Create server_2 on subnet_2 and hosted on the same compute

    **Steps:**

    #. Ping server_2 from server_1
    #. Ping server_1 from server_2

    **Teardown:**

    #. Delete servers
    #. Delete router, subnets and network
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_1, server_2 = neutron_2_servers_different_subnets.servers

    for server_init, server_dest in ((server_1, server_2),
                                     (server_2, server_1)):
        proxy_cmd = get_ssh_proxy_cmd(server_init)
        server_dest_ip = server_steps.get_fixed_ip(server_init)
        with server_steps.get_server_ssh(
                server_init, proxy_cmd=proxy_cmd) as server_init_ssh:
            server_steps.check_ping_for_ip(
                server_dest_ip,
                server_init_ssh,
                timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
