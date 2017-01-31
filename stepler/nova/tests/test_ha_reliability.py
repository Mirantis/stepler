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
                                 rabbitmq_steps,
                                 get_rabbitmq_cluster_data,
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
    #. Create floating IP
    #. Create volume

    **Steps:**

    #. Start Openstack workload generation (optional)
    #. Get current states of Nova services and Galera
    #. Check status of RabbitMQ cluster
    #. Shutdown controller holding VIP
    #. Wait until basic OpenStack operations start working
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Turn on controller holding VIP
    #. Wait until basic OpenStack operations start working
    #. Check Galera state
    #. Check status of RabbitMQ cluster

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

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    cluster_node_names, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

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

    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)


@platform.mk2x
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
                           rabbitmq_steps,
                           get_rabbitmq_cluster_data,
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

    #. Get current states of Nova services and Galera
    #. Check status of RabbitMQ cluster
    #. Power off the all nodes at once
    #. Wait for 5 minutes
    #. Start all cluster nodes one by one
    #. Wait until basic OpenStack operations start working
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check Galera state
    #. Check status of RabbitMQ cluster

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
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    cluster_node_names, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

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

    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)


@platform.mk2x
@pytest.mark.idempotent_id('7509ac93-f0a3-4b62-84dc-ed722e3eba55')
def test_network_outage(cirros_image,
                        keypair,
                        flavor,
                        security_group,
                        net_subnet_router,
                        nova_floating_ip,
                        volume,
                        attach_volume_to_server,
                        router_steps,
                        server_steps,
                        nova_service_steps,
                        rabbitmq_steps,
                        get_rabbitmq_cluster_data,
                        os_faults_steps):
    """**Scenario:** Check functionality after network outage

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP
    #. Create volume

    **Steps:**

    #. Get current states of Nova services and Galera
    #. Check status of RabbitMQ cluster
    #. Switch off ports on router
    #. Wait for 5 minutes
    #. Switch on ports
    #. Wait until basic OpenStack operations start working
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check Galera state
    #. Check status of RabbitMQ cluster

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

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    cluster_node_names, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

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

    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)


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
                               rabbitmq_steps,
                               get_rabbitmq_cluster_data,
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
    #. Create floating IP
    #. Create volume

    **Steps:**

    #. Start Openstack workload generation (optional)
    #. Get current states of Nova services and Galera
    #. Check status of RabbitMQ cluster
    #. Reboot controller holding VIP
    #. Wait until basic OpenStack operations start working
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check Galera state
    #. Check status of RabbitMQ cluster

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

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    cluster_node_names, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

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

    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)


@platform.mk2x
@pytest.mark.idempotent_id('76a612ca-98ae-4808-b5cc-9a8718991464',
                           os_workload=False)
@pytest.mark.idempotent_id('5814e237-0acd-493b-b97b-8e6d5829a50f',
                           os_workload=True)
@pytest.mark.parametrize('os_workload', [False, True],
                         ids=['without workload', 'with workload'])
def test_stop_rabbitmq(cirros_image,
                       keypair,
                       flavor,
                       security_group,
                       net_subnet_router,
                       nova_floating_ip,
                       attach_volume_to_server,
                       volume,
                       server_steps,
                       rabbitmq_steps,
                       get_rabbitmq_cluster_data,
                       os_faults_steps,
                       generate_os_workload,
                       os_workload):
    """**Scenario:** Check functionality after stopping RabbitMQ on one node

    This test has two modes: with and without Openstack workload

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP
    #. Create volume

    **Steps:**

    #. Start Openstack workload generation (optional)
    #. Check Galera state
    #. Check status of RabbitMQ cluster
    #. Stop RabbitMQ service on one node
    #. Wait 3 minutes
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check status of RabbitMQ cluster
    #. Check traffic on RabbitMQ nodes
    #. Start RabbitMQ service
    #. Check status of RabbitMQ cluster
    #. Check traffic on RabbitMQ nodes
    #. Check Galera state

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

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    cluster_node_names, fqdns, ip_addresses, cluster_status = (
        get_rabbitmq_cluster_data())
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

    disabled_fqdn = fqdns[0]
    disabled_node = os_faults_steps.get_node(fqdns=[disabled_fqdn])
    os_faults_steps.terminate_service(service_name=config.RABBITMQ,
                                      nodes=disabled_node)

    time.sleep(config.TIME_AFTER_RABBITMQ_STOP)

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

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names,
                                        disabled_nodes_number=1)

    rabbitmq_steps.check_traffic(ip_addresses,
                                 disabled_ip_address=ip_addresses[0])

    os_faults_steps.start_service(service_name=config.RABBITMQ,
                                  nodes=disabled_node)

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

    rabbitmq_steps.check_traffic(ip_addresses)

    os_faults_steps.check_service_state(service_name=config.MYSQL,
                                        nodes=mysql_nodes)


@platform.mk2x
@pytest.mark.idempotent_id('d445284f-4029-489e-b3d8-2495a4092d28',
                           os_workload=False)
@pytest.mark.idempotent_id('238e32a2-9d85-45fb-8a6b-1b2b26d74fcc',
                           os_workload=True)
@pytest.mark.parametrize('os_workload', [False, True],
                         ids=['without workload', 'with workload'])
def test_unplug_network(cirros_image,
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
    """**Scenario:** Check functionality after network unpluging on mysql node

    This test has two modes: with and without Openstack workload

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP
    #. Create volume

    **Steps:**

    #. Start Openstack workload generation (optional)
    #. Check Galera state
    #. Down network interfaces on MySQL node and schedule its up in 3 minutes
    #. Wait for nova services work on available nodes
    #. Check Galera state and data replication on available nodes
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Wait for network interfaces up
    #. Wait for nova services work on all nodes
    #. Check Galera state

    **Teardown:**

    #. Stop Openstack workload generation
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

    nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=nodes)

    disabled_node = os_faults_steps.get_node(fqdns=[nodes.hosts[0].fqdn])
    enabled_nodes = nodes - disabled_node

    os_faults_steps.down_interfaces(disabled_node,
                                    duration=config.TIME_INTERFACE_DOWN)
    interface_up_time = time.time() + config.TIME_INTERFACE_DOWN

    enabled_host_names = [host_steps.get_host(fqdn=node.fqdn).host_name
                          for node in enabled_nodes]
    nova_service_steps.check_services_up(
        host_names=enabled_host_names,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    os_faults_steps.check_galera_cluster_state(member_nodes=enabled_nodes)
    os_faults_steps.check_galera_data_replication(enabled_nodes)

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

    interface_up_delay = interface_up_time - time.time()
    if interface_up_delay > 0:
        time.sleep(interface_up_delay)

    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)

    os_faults_steps.check_galera_cluster_state(member_nodes=nodes)


@platform.mk2x
@pytest.mark.idempotent_id('509fa960-c42c-40de-bbc5-61b59391b9c5',
                           stop_command=config.STOP_KEEPALIVED_CMD)
@pytest.mark.idempotent_id('b18754ba-a0c4-4b58-9e7e-1000b0c32ae9',
                           stop_command=config.KILL9_KEEPALIVED_CMD)
@pytest.mark.parametrize('stop_command',
                         [config.STOP_KEEPALIVED_CMD,
                          config.KILL9_KEEPALIVED_CMD],
                         ids=['stop', 'kill-9'])
def test_stop_keepalived(cirros_image,
                         keypair,
                         flavor,
                         security_group,
                         net_subnet_router,
                         nova_floating_ip,
                         attach_volume_to_server,
                         volume,
                         server_steps,
                         rabbitmq_steps,
                         get_rabbitmq_cluster_data,
                         execute_command_with_rollback,
                         os_faults_steps,
                         generate_os_workload,
                         stop_command):
    """**Scenario:** Check functionality after stopping keepalived on VIP node

    Keepalived is stopped by 'stop' or 'kill -9'.
    This test is executed under Openstack workload.

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create flavor
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP
    #. Create volume

    **Steps:**

    #. Start Openstack workload generation
    #. Check Galera state
    #. Check status of RabbitMQ cluster
    #. Stop/kill keepalived on controller holding VIP
    #. Check traffic on RabbitMQ nodes
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check Galera state
    #. Start keepalived on controller holding VIP

    **Teardown:**

    #. Stop Openstack workload generation
    #. Delete volume
    #. Delete server
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    generate_os_workload(config.OS_LOAD_GENERATOR)

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])

    cluster_node_names, _, ip_addresses, cluster_status = (
        get_rabbitmq_cluster_data())
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

    vip_controller = os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)

    with execute_command_with_rollback(
            nodes=vip_controller,
            cmd=stop_command,
            rollback_cmd=config.START_KEEPALIVED_CMD):

        time.sleep(config.TIME_AFTER_KEEPALIVED_STOP)

        _, _, _, cluster_status = get_rabbitmq_cluster_data()
        rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

        rabbitmq_steps.check_traffic(ip_addresses)

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

        os_faults_steps.check_service_state(service_name=config.MYSQL,
                                            nodes=mysql_nodes)

    time.sleep(config.TIME_AFTER_KEEPALIVED_START)


@platform.mk2x
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

    #. Terminate 'mysql' service on all nodes
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
    secondary_nodes = mysql_nodes - primary_node

    # Start galera cluster
    os_faults_steps.execute_cmd(primary_node, config.GALERA_CLUSTER_START_CMD)
    os_faults_steps.check_galera_cluster_state(member_nodes=primary_node)

    # Add secondary nodes to cluster
    os_faults_steps.start_service(service_name=config.MYSQL,
                                  nodes=secondary_nodes)
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)
    server_steps.create_servers(image=cirros_image,
                                flavor=flavor,
                                networks=[net_subnet_router[0]])


@platform.mk2x
@pytest.mark.idempotent_id('c2b89348-30a6-43b1-b547-9d8615f22e29')
def test_reboot_node_from_galera_cluster_with_load(generate_os_workload,
                                                   cirros_image,
                                                   flavor,
                                                   net_subnet_router,
                                                   os_faults_steps,
                                                   server_steps):
    """**Scenario:** Check reboot node from galera cluster with workload.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create network, subnet and router

    **Steps:**

    #. Start Openstack workload generation
    #. Reset one node from Galera cluster
    #. Check that Galera cluster still operational but without rebooted node
    #. Wait for Galera cluster update after node availability
    #. Check cluster state and size
    #. Create server to check cluster operability

    **Teardown:**

    #. Stop Openstack workload generation
    #. Delete server
    #. Delete network, subnet and router
    #. Delete flavor
    #. Delete cirros image
    """
    generate_os_workload(config.OS_LOAD_GENERATOR)
    nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    node_to_reboot = os_faults_steps.get_node(fqdns=[nodes.hosts[0].fqdn])
    other_nodes = nodes - node_to_reboot

    os_faults_steps.reset_nodes(node_to_reboot)
    os_faults_steps.check_galera_cluster_state(member_nodes=other_nodes)

    time.sleep(config.GALERA_CLUSTER_UP_TIMEOUT)

    os_faults_steps.check_galera_cluster_state(member_nodes=nodes)
    server_steps.create_servers(image=cirros_image,
                                flavor=flavor,
                                networks=[net_subnet_router[0]])


@platform.mk2x
@pytest.mark.idempotent_id('e85c3844-e4ce-48d4-8dd6-0605e65001fb')
def test_fill_root_filesystem_on_vip_controller(server,
                                                os_faults_steps,
                                                server_steps,
                                                get_server_steps):
    """**Scenario:** Check Galera cluster after free up space on controller.

    This test checks OpenStack operations fail in case of no free space on
    controller holding VIP. Also it checks cluster is in working state after
    space has been freed.

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
    file_path = file_dir + next(utils.generate_ids())
    vip_controller = os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)

    server_steps.get_servers()

    free_space = os_faults_steps.get_free_space(vip_controller, file_dir)
    cmd = config.CREATE_FILE_CMD.format(size=free_space, file_path=file_path)
    os_faults_steps.execute_cmd(vip_controller, cmd)
    server_steps.check_servers_actions_not_available(get_server_steps)

    cmd = config.REMOVE_FILE_CMD.format(file_path=file_path)
    os_faults_steps.execute_cmd(vip_controller, cmd)
    server_steps = get_server_steps()
    server_steps.get_servers()
