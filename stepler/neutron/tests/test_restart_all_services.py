"""
----------------------------
Restart all neutron services
----------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from stepler import config
from stepler.third_party import utils

pytestmark = pytest.mark.destructive


@pytest.mark.idempotent_id('ef846e7b-b96c-43ae-87f8-73d542821909')
def test_restart_all_neutron_services(ubuntu_image,
                                      keypair,
                                      flavor,
                                      security_group,
                                      net_subnet_router,
                                      nova_create_floating_ip,
                                      os_faults_steps,
                                      create_network,
                                      create_subnet,
                                      create_router,
                                      add_router_interfaces,
                                      server_steps):
    """**Scenario:** Restart all Neutron services.

    **Setup:**

    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1

    **Steps:**

    #. Boot server_1 and associate floating IP
    #. Check that ping from server_1 to 8.8.8.8 is successful
    #. Restart all running neutron services on controllers
    #. Restart all running neutron services on computes
    #. Boot server_2 and associate floating IP
    #. Check ping between server_1 and server_2 and ping to 8.8.8.8
    #. Create new network "net01" and router between "net01" and external net
    #. Boot server_3 and associate floating IP on network "net01"
    #. Check that ping from server_3 to 8.8.8.8 is successful
    #. Delete all servers

    **Teardown:**

    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete security group
    #. Delete flavor
    #. Delete keypair

    """
    net, _, _ = net_subnet_router
    controllers = os_faults_steps.get_nodes(
        service_names=[config.NEUTRON_DHCP_SERVICE])
    computes = os_faults_steps.get_nodes(
        service_names=[config.NEUTRON_OVS_SERVICE])
    server_1 = server_steps.create_servers(image=ubuntu_image,
                                           flavor=flavor,
                                           networks=[net],
                                           security_groups=[security_group],
                                           username=config.UBUNTU_USERNAME,
                                           keypair=keypair)[0]
    server_steps.attach_floating_ip(server_1, nova_create_floating_ip())
    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh,
            timeout=config.PING_CALL_TIMEOUT)
    services_on_controllers = os_faults_steps.get_services_for_component(
        component=config.NEUTRON, nodes=controllers)
    for host in controllers:
        node = os_faults_steps.get_node(fqdns=[host.fqdn])
        os_faults_steps.restart_services(
            names=services_on_controllers[host.fqdn], nodes=node)
    services_on_computes = os_faults_steps.get_services_for_component(
        component='neutron', nodes=computes)
    for host in computes:
        node = os_faults_steps.get_node(fqdns=[host.fqdn])
        os_faults_steps.restart_services(names=services_on_computes[host.fqdn],
                                         nodes=node)
    server_2 = server_steps.create_servers(image=ubuntu_image,
                                           flavor=flavor,
                                           networks=[net],
                                           security_groups=[security_group],
                                           username=config.UBUNTU_USERNAME,
                                           keypair=keypair)[0]
    server_steps.attach_floating_ip(server_2, nova_create_floating_ip())
    server_steps.check_ping_between_servers_via_floating(
       [server_1, server_2], timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
    network_2 = create_network(next(utils.generate_ids()))
    subnet = create_subnet(next(utils.generate_ids()),
                           network_2,
                           cidr="192.168.2.0/24")
    router_2 = create_router(next(utils.generate_ids()))
    add_router_interfaces(router_2, [subnet])
    server_3 = server_steps.create_servers(image=ubuntu_image,
                                           flavor=flavor,
                                           networks=network_2,
                                           security_groups=[security_group],
                                           username=config.UBUNTU_USERNAME,
                                           keypair=keypair)[0]
    server_steps.attach_floating_ip(server_3, nova_create_floating_ip())
    with server_steps.get_server_ssh(server_3) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh,
            timeout=config.PING_CALL_TIMEOUT)
    server_steps.delete_servers([server_1, server_2, server_3])
