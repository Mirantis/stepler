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
def test_check_connectivity_between_servers_same_network(
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
        server_dest_ip = next(iter(server_steps.get_ips(server_dest,
                                                        config.FIXED_IP)))
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
def test_check_connectivity_between_servers_diff_networks(
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
        server_dest_ip = next(iter(server_steps.get_ips(server_dest,
                                                        config.FIXED_IP)))
        with server_steps.get_server_ssh(
                server_init, proxy_cmd=proxy_cmd) as server_init_ssh:
            server_steps.check_ping_for_ip(
                server_dest_ip,
                server_init_ssh,
                timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
