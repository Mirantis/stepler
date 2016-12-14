"""
-------------------------
Restart all nova services
-------------------------
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


@pytest.mark.idempotent_id('03c7bd50-0f78-4dd2-888f-a1e647f8c20e')
def test_restart_all_nova_services(cirros_image,
                                   flavor,
                                   security_group,
                                   net_subnet_router,
                                   nova_create_floating_ip,
                                   os_faults_steps,
                                   server_steps):
    """**Scenario:** Restart all Nova services.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1

    **Steps:**

    #. Boot server_1 and associate floating IP
    #. Check that ping from server_1 to 8.8.8.8 is successful
    #. Restart all running nova services on controllers
    #. Boot server_2 and associate floating IP
    #. Check ping between server_1 and server_2 and ping to 8.8.8.8
    #. Restart all running nova services on computes
    #. Boot server_3 and associate floating IP
    #. Check ping between server_1, server_2, server_3 and ping to 8.8.8.8
    #. Restart all running nova services
    #. Check ping between server_1, server_2, server_3 and ping to 8.8.8.8
    #. Delete all servers

    **Teardown:**

    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete security group
    #. Delete cirros image

    """
    net, _, _ = net_subnet_router
    controllers = os_faults_steps.get_nodes(service_names=[config.NOVA_API])
    computes = os_faults_steps.get_nodes(service_names=[config.NOVA_COMPUTE])

    server_create_args = dict(
        image=cirros_image,
        flavor=flavor,
        networks=[net],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD)

    # Boot server_1 and check ping
    server_1 = server_steps.create_servers(**server_create_args)[0]
    server_steps.attach_floating_ip(server_1, nova_create_floating_ip())
    with server_steps.get_server_ssh(server_1) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh,
            timeout=config.PING_CALL_TIMEOUT)

    nova_services = os_faults_steps.get_services_names(name_prefix='nova')
    # Restart nova services on controllers
    os_faults_steps.restart_services(names=nova_services, nodes=controllers,
                                     check=False)

    server_2 = server_steps.create_servers(**server_create_args)[0]
    server_steps.attach_floating_ip(server_2, nova_create_floating_ip())
    ping_plan = {
        server_1: [config.GOOGLE_DNS_IP, (server_2, config.FLOATING_IP)],
        server_2: [config.GOOGLE_DNS_IP, (server_1, config.FLOATING_IP)]}
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    # Restart nova services on computes
    os_faults_steps.restart_services(names=nova_services, nodes=computes,
                                     check=False)

    server_3 = server_steps.create_servers(**server_create_args)[0]
    server_steps.attach_floating_ip(server_3, nova_create_floating_ip())
    ping_plan = {server_1: [config.GOOGLE_DNS_IP,
                            (server_2, config.FLOATING_IP),
                            (server_3, config.FLOATING_IP)],
                 server_2: [config.GOOGLE_DNS_IP,
                            (server_1, config.FLOATING_IP),
                            (server_3, config.FLOATING_IP)],
                 server_3: [config.GOOGLE_DNS_IP,
                            (server_1, config.FLOATING_IP),
                            (server_2, config.FLOATING_IP)]}
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    # Restart all nova services
    os_faults_steps.restart_services(names=nova_services,
                                     nodes=controllers | computes,
                                     check=False)
    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    server_steps.delete_servers([server_1, server_2, server_3])
