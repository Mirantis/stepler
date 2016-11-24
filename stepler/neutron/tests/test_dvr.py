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
@pytest.mark.idempotent_id(
    '91853195-c456-464c-b0a4-5655acee7769',
    router=dict(distributed=True),
    neutron_2_servers_different_networks='same_host')
@pytest.mark.idempotent_id(
    '8dd82992-136b-4a46-b399-74a12bb16613',
    router=dict(distributed=True),
    neutron_2_servers_different_networks='different_hosts')
@pytest.mark.idempotent_id(
    '808b1d0c-e492-4a26-97b3-758c0baace80',
    router=dict(distributed=False),
    neutron_2_servers_different_networks='different_hosts')
@pytest.mark.parametrize(
    'router, neutron_2_servers_different_networks',
    [(dict(distributed=True), 'same_host'),
     (dict(distributed=True), 'different_hosts'),
     (dict(distributed=False), 'different_hosts')],
    ids=['distributed router, same host',
         'distributed router, different hosts',
         'centralized router, different hosts'],
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
