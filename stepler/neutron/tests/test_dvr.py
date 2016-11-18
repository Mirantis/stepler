"""
-------------
Neutron tests
-------------
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
from stepler.third_party import utils


@pytest.mark.idempotent_id('91853195-c456-464c-b0a4-5655acee7769')
def test_check_connectivity_to_west_east_routing(create_network,
                                                 create_subnet,
                                                 create_router,
                                                 public_network,
                                                 add_router_interfaces,
                                                 router_steps,
                                                 flavor,
                                                 security_group,
                                                 cirros_image,
                                                 nova_floating_ip,
                                                 server_steps,
                                                 hypervisor_steps):
    """**Scenario:** Check connectivity to West-East-Routing.

    **Setup:**

    #. Create flavor
    #. Create security group with allow ping rule
    #. Upload cirros image

    **Steps:**

    #. Create networks net_1 and net_2 with subnets
    #. Create distributed virtual router
    #. Set router default gateway to public network
    #. Add interfaces to the router with subnet_1 and subnet_2
    #. Boot 2 servers from cirros image on different computes
    #. Assign floating ip to server_1
    #. Check that ping from server_1 to server_2 is successful

    **Teardown:**

    #. Delete servers
    #. Delete flavor
    #. Delete security group
    #. Delete cirros image
    #. Delete router
    #. Delete subnets
    #. Delete networks
    """
    net_1 = create_network(next(utils.generate_ids()))
    subnet_1 = create_subnet(next(utils.generate_ids()),
                             net_1,
                             cidr='10.1.1.0/24')
    net_2 = create_network(next(utils.generate_ids()))
    subnet_2 = create_subnet(next(utils.generate_ids()),
                             net_2,
                             cidr='10.1.2.0/24')
    router = create_router(next(utils.generate_ids()),
                           distributed=True)
    router_steps.set_gateway(router, public_network)
    add_router_interfaces(router, [subnet_1, subnet_2])

    hypervisors = hypervisor_steps.get_hypervisors()
    server_1 = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[net_1],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD,
        availability_zone='nova:{}'.format(hypervisors[0].hypervisor_hostname)
    )[0]
    server_2 = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[net_2],
        security_groups=[security_group],
        availability_zone='nova:{}'.format(hypervisors[1].hypervisor_hostname)
    )[0]

    server_steps.attach_floating_ip(server_1, nova_floating_ip)
    server_2_ip = next(iter(server_steps.get_ips(server_2,
                                                 config.FIXED_IP)))
    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            server_2_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
