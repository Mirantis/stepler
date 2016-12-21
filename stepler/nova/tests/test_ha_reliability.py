"""
--------------------
HA reliability tests
--------------------
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


@pytest.mark.idempotent_id('6d8cfa5c-c927-4916-940e-5dd57c8e8977')
def test_shutdown_vip_controller(cirros_image,
                                 keypair,
                                 flavor,
                                 security_group,
                                 net_subnet_router,
                                 nova_create_floating_ip,
                                 server_steps,
                                 nova_service_steps,
                                 os_faults_steps):
    """**Scenario:** Check functionality after shutdown of controller with VIP

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router

    **Steps:**

    #. Get current states of Nova services, RabbitMQ and Galera
    #. Shutdown controller holding VIP
    #. Wait until basic OpenStack operations start working
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Turn on controller holding VIP
    #. Wait until basic OpenStack operations start working
    #. Check RabbitMQ and Galera states

    **Teardown:**

    #. Delete server
    #. Delete network, subnet, router
    #. Delete floating IP
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    nova_services_init = nova_service_steps.get_services()

    rabbit_nodes = os_faults_steps.get_nodes(service_names=[config.RABBITMQ])
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    # vip_controller =
    os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)

    # TODO(ssokolov) commented because poweron is not yet implemented
    # os_faults_steps.poweroff_nodes(vip_controller)

    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]

    floating_ip = nova_create_floating_ip()
    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(server, floating_ip.ip) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP,
                                       server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)

    # TODO(ssokolov) not yet implemented
    # os_faults_steps.poweron_nodes(vip_controller)

    nova_service_steps.check_service_states(
        nova_services_init,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    os_faults_steps.check_service_state(service_name=config.RABBITMQ,
                                        nodes=rabbit_nodes)
    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)


@pytest.mark.idempotent_id('8544c689-481c-4c1c-9163-3fad0803813a')
def test_reboot_vip_controller(cirros_image,
                               keypair,
                               flavor,
                               security_group,
                               net_subnet_router,
                               nova_create_floating_ip,
                               server_steps,
                               nova_service_steps,
                               os_faults_steps):
    """**Scenario:** Check functionality after reboot of controller with VIP

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router

    **Steps:**

    #. Get current states of nova services, RabbitMQ and Galera
    #. Reboot controller holding VIP
    #. Wait until basic OpenStack operations start working
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check RabbitMQ and Galera states

    **Teardown:**

    #. Delete server
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    nova_services_init = nova_service_steps.get_services()

    rabbit_nodes = os_faults_steps.get_nodes(service_names=[config.RABBITMQ])
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    vip_controller = os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)

    os_faults_steps.execute_cmd(vip_controller, config.NODE_REBOOT_CMD)
    os_faults_steps.check_nodes_tcp_availability(
        vip_controller,
        must_available=False,
        timeout=config.NODE_SHUTDOWN_TIMEOUT)
    os_faults_steps.check_nodes_tcp_availability(
        vip_controller,
        must_available=True,
        timeout=config.NODE_REBOOT_TIMEOUT)

    nova_service_steps.check_service_states(
        nova_services_init,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]

    floating_ip = nova_create_floating_ip()
    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(server, floating_ip.ip) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP,
                                       server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.check_service_state(service_name=config.RABBITMQ,
                                        nodes=rabbit_nodes)
    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)
