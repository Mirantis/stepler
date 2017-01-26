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

import time

import pytest

from stepler import config
from stepler.third_party.supported_platforms import platform
from stepler.third_party import utils


pytestmark = pytest.mark.destructive


@platform.mk2x
@pytest.mark.idempotent_id('6d8cfa5c-c927-4916-940e-5dd57c8e8977',
                           os_workload=False)
@pytest.mark.idempotent_id('2afbfd6f-d087-47db-81af-dea23b8c47ad',
                           os_workload=True)
@pytest.mark.parametrize('os_workload', [False, True],
                         ids=['without workload', 'with workload'])
def test_shutdown_vip_controller(cirros_image,
                                 keypair,
                                 flavor,
                                 security_group,
                                 net_subnet_router,
                                 nova_floating_ip,
                                 attach_volume_to_server,
                                 volume,
                                 server_steps,
                                 nova_service_steps,
                                 host_steps,
                                 os_faults_steps,
                                 generate_os_workload,
                                 os_workload):
    """**Scenario:** Check functionality after shutdown of controller with VIP

    This test has two modes: with and without Openstack workload

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router
    #. Create volume
    #. Create floating IP

    **Steps:**

    #. Start Openstack workload generation (optional)
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

    #. Stop Openstack workload generation (optional)
    #. Delete volume
    #. Delete server
    #. Delete network, subnet, router
    #. Delete floating IP
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    if os_workload:
        generate_os_workload(config.OS_LOAD_GENERATOR)

    nova_services_init = nova_service_steps.get_services()

    rabbit_nodes = os_faults_steps.get_nodes(service_names=[config.RABBITMQ])
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    nova_nodes = os_faults_steps.get_nodes_with_any_service(
        [config.NOVA_API, config.NOVA_COMPUTE])
    vip_controller = os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)
    nodes_without_vip = nova_nodes - vip_controller
    alive_host_names = [host_steps.get_host(fqdn=node.fqdn).host_name for
                        node in nodes_without_vip]

    os_faults_steps.poweroff_nodes(vip_controller)

    nova_service_steps.check_services_up(
        host_names=alive_host_names,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, nova_floating_ip)

    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP,
                                       server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.poweron_nodes(vip_controller)

    nova_service_steps.check_service_states(
        nova_services_init,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    os_faults_steps.check_service_state(service_name=config.RABBITMQ,
                                        nodes=rabbit_nodes)
    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)


@pytest.mark.idempotent_id('75d405d0-1f31-498c-b144-3b160b85a39e')
def test_power_off_cluster(cirros_image,
                           keypair,
                           flavor,
                           security_group,
                           net_subnet_router,
                           nova_floating_ip,
                           attach_volume_to_server,
                           volume,
                           get_nova_client,
                           nova_service_steps,
                           server_steps,
                           os_faults_steps):
    """**Scenario:** Check functionality after power off/on the whole cluster

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router
    #. Create volume
    #. Create floating IP

    **Steps:**

    #. Get current states of nova services, RabbitMQ and Galera
    #. Power off the all nodes at once
    #. Wait for 5 minutes
    #. Start all cluster nodes one by one
    #. Wait until basic OpenStack operations start working
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check RabbitMQ and Galera states

    **Teardown:**

    #. Delete volume
    #. Delete server
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    rabbit_nodes = os_faults_steps.get_nodes(service_names=[config.RABBITMQ])
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    nodes = os_faults_steps.get_nodes()

    os_faults_steps.poweroff_nodes(nodes)

    time.sleep(config.TIME_BETWEEN_CLUSTER_RESTART)

    # TODO(ssokolov): replace when os-faults supports 'for node in nodes'
    # for node in nodes:
    #     os_faults_steps.poweron_nodes(node)
    for fqdn in [node.fqdn for node in nodes]:
        node = os_faults_steps.get_nodes(fqdns=[fqdn])
        os_faults_steps.poweron_nodes(node)

    # reinit nova client and wait for its availability
    get_nova_client()

    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, nova_floating_ip)

    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP,
                                       server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.check_service_state(service_name=config.RABBITMQ,
                                        nodes=rabbit_nodes)
    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)


@pytest.mark.idempotent_id('7509ac93-f0a3-4b62-84dc-ed722e3eba55')
def test_network_outage(cirros_image,
                        keypair,
                        flavor,
                        security_group,
                        net_subnet_router,
                        volume,
                        nova_floating_ip,
                        attach_volume_to_server,
                        router_steps,
                        server_steps,
                        nova_service_steps,
                        os_faults_steps):
    """**Scenario:** Check functionality after network outage

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router
    #. Create volume
    #. Create floating IP

    **Steps:**

    #. Get current states of nova services, RabbitMQ and Galera
    #. Switch off ports on router
    #. Wait for 5 minutes
    #. Switch on ports
    #. Wait until basic OpenStack operations start working
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check RabbitMQ and Galera states

    **Teardown:**

    #. Delete volume
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

    network, _, router = net_subnet_router
    router_steps.update_router(router, admin_state_up=False)

    time.sleep(config.NETWORK_OUTAGE_TIME)

    router_steps.update_router(router, admin_state_up=True)

    nova_service_steps.check_service_states(
        nova_services_init,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=flavor,
                                         networks=[network],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, nova_floating_ip)

    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP,
                                       server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.check_service_state(service_name=config.RABBITMQ,
                                        nodes=rabbit_nodes)
    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)


@platform.mk2x
@pytest.mark.idempotent_id('8544c689-481c-4c1c-9163-3fad0803813a',
                           os_workload=False)
@pytest.mark.idempotent_id('3cd46899-528e-4c58-9841-2189bb23f7ba',
                           os_workload=True)
@pytest.mark.parametrize('os_workload', [False, True],
                         ids=['without workload', 'with workload'])
def test_reboot_vip_controller(cirros_image,
                               keypair,
                               flavor,
                               security_group,
                               net_subnet_router,
                               nova_floating_ip,
                               attach_volume_to_server,
                               volume,
                               server_steps,
                               nova_service_steps,
                               os_faults_steps,
                               generate_os_workload,
                               os_workload):
    """**Scenario:** Check functionality after reboot of controller with VIP

    This test has two modes: with and without Openstack workload

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router
    #. Create volume
    #. Create floating IP

    **Steps:**

    #. Start Openstack workload generation (optional)
    #. Get current states of nova services, RabbitMQ and Galera
    #. Reboot controller holding VIP
    #. Wait until basic OpenStack operations start working
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check RabbitMQ and Galera states

    **Teardown:**

    #. Stop Openstack workload generation (optional)
    #. Delete volume
    #. Delete server
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    if os_workload:
        generate_os_workload(config.OS_LOAD_GENERATOR)

    nova_services_init = nova_service_steps.get_services()

    rabbit_nodes = os_faults_steps.get_nodes(service_names=[config.RABBITMQ])
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    vip_controller = os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)

    os_faults_steps.reset_nodes(vip_controller)

    nova_service_steps.check_service_states(
        nova_services_init,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, nova_floating_ip)

    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP,
                                       server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.check_service_state(service_name=config.RABBITMQ,
                                        nodes=rabbit_nodes)
    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)


@platform.mk2x
@pytest.mark.idempotent_id('e85c3844-e4ce-48d4-8dd6-0605e65001fb')
def test_fill_root_filesystem_on_vip_controller(server,
                                                os_faults_steps,
                                                server_steps,
                                                get_server_steps):
    """**Scenario:** Check functionality after reboot of controller with VIP

    This test has two modes: with and without Openstack workload

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router
    #. Create server

    **Steps:**

    #. Find controller holding VIP
    #. Check basic openstack operation: request server list
    #. Allocate all free space on controller
    #. Check that openstack operations failed with GatewayTimeout exception
    #. Free up disk space on controller
    #. Check basic openstack operation: request server list

    **Teardown:**

    #. Delete server
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    file_dir = '/'
    file_name = next(utils.generate_ids())
    vip_controller = os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)
    vip_controller_ip = vip_controller.get_ips()[0]

    server_steps.get_servers()

    free_space = os_faults_steps.get_free_space(vip_controller, file_dir)
    cmd = 'fallocate -l {}K {}{}'.format(free_space[vip_controller_ip],
                                         file_dir, file_name)
    os_faults_steps.execute_cmd(vip_controller, cmd)
    server_steps.check_servers_actions_not_available(get_server_steps)

    cmd = "rm -f {}{}".format(file_dir, file_name)
    os_faults_steps.execute_cmd(vip_controller, cmd)
    server_steps = get_server_steps()
    server_steps.get_servers()
