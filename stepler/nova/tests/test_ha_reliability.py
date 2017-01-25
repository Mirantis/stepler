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
                                 volume,
                                 nova_floating_ip,
                                 attach_volume_to_server,
                                 server_steps,
                                 nova_service_steps,
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

    # TODO(ssokolov) uncomment after fixing poweron/poweroff problem
    # vip_controller = os_faults_steps.get_nodes_by_cmd(
    #     config.TCP_VIP_CONTROLLER_CMD)

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
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, nova_floating_ip)

    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
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


@platform.mk2x
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
                               volume,
                               nova_floating_ip,
                               attach_volume_to_server,
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

    # TODO(ssokolov) can be replaced to os_faults_steps.reset()
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
@pytest.mark.destructive
@pytest.mark.idempotent_id('bcb88d70-d347-45fa-9261-71732ac54523')
def test_shutdown_and_bootstrap_galera_cluster(cirros_image,
                                               flavor,
                                               net_subnet_router,
                                               os_faults_steps,
                                               server_steps):
    """**Scenario:** Check shutdown and bootstrap galera cluster.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create network, subnet and router

    **Steps:**

    #. Terminate 'mysql' service for all nodes
    #. Run '/usr/bin/mysqld_safe --wsrep-new-cluster' on the one node
    #. Check that new operational cluster is created and its size 1
    #. Add nodes to cluster by start of 'mysql' service
    #. Check that cluster still operational but with new size
    #. Create server to check cluster

    **Teardown:**

    #. Delete server
    #. Delete network, subnet and router
    #. Delete flavor
    #. Delete cirros image
    """
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.terminate_service(service_name=config.MYSQL,
                                      nodes=mysql_nodes)

    primary_node = os_faults_steps.get_node(fqdns=[mysql_nodes.hosts[0].fqdn])
    secondary_node_fqdns = [host.fqdn for host in mysql_nodes.hosts[1:]]
    secondary_nodes = os_faults_steps.get_nodes(fqdns=secondary_node_fqdns)

    # Start galera cluster
    os_faults_steps.execute_cmd(primary_node, config.GALERA_CLUSTER_START_CMD)
    os_faults_steps.check_galera_cluster_state(primary_node, 1)

    # Add secondary nodes to cluster
    os_faults_steps.start_service(service_name=config.MYSQL,
                                  nodes=secondary_nodes)
    os_faults_steps.check_galera_cluster_state(mysql_nodes, len(mysql_nodes))

    server_steps.create_servers(image=cirros_image,
                                flavor=flavor,
                                networks=[net_subnet_router[0]],
                                username=config.CIRROS_USERNAME,
                                password=config.CIRROS_PASSWORD)
