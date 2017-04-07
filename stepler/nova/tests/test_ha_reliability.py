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


@platform.mcp
@pytest.mark.idempotent_id('6d8cfa5c-c927-4916-940e-5dd57c8e8977',
                           os_workload=False)
@pytest.mark.idempotent_id('2afbfd6f-d087-47db-81af-dea23b8c47ad',
                           os_workload=True)
@pytest.mark.parametrize('os_workload', [False, True],
                         ids=['without workload', 'with workload'])
def test_shutdown_vip_controller(cirros_image,
                                 keypair,
                                 tiny_flavor,
                                 security_group,
                                 net_subnet_router,
                                 floating_ip,
                                 attach_volume_to_server,
                                 volume_steps,
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
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Start Openstack workload generation (optional)
    #. Check Galera state
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
    #. Delete server
    #. Delete volume
    #. Delete network, subnet, router
    #. Delete floating IP
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    if os_workload:
        generate_os_workload(config.OS_LOAD_GENERATOR)

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    cluster_node_names, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

    nova_nodes = os_faults_steps.get_nodes_with_any_service(
        [config.NOVA_API, config.NOVA_COMPUTE])
    vip_controller = os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)
    nodes_without_vip = nova_nodes - vip_controller
    alive_host_names = [host_steps.get_host(fqdn=node.fqdn).host_name for
                        node in nodes_without_vip]

    os_faults_steps.shutdown_nodes(vip_controller)

    nova_service_steps.check_services_up(
        host_names=alive_host_names,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=tiny_flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    volume = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.poweron_nodes(vip_controller)

    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)


@platform.mcp
@pytest.mark.idempotent_id('75d405d0-1f31-498c-b144-3b160b85a39e')
def test_power_off_cluster(cirros_image,
                           keypair,
                           tiny_flavor,
                           security_group,
                           net_subnet_router,
                           floating_ip,
                           attach_volume_to_server,
                           volume_steps,
                           server_steps,
                           get_nova_client,
                           nova_service_steps,
                           rabbitmq_steps,
                           get_rabbitmq_cluster_data,
                           os_faults_steps):
    """**Scenario:** Check functionality after power off/on the whole cluster

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Check Galera state
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

    #. Delete server
    #. Delete volume
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    cluster_node_names, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

    nodes = os_faults_steps.get_nodes()

    os_faults_steps.poweroff_nodes(nodes)

    time.sleep(config.TIME_BETWEEN_CLUSTER_RESTART)

    for fqdn in [node.fqdn for node in nodes]:
        node = os_faults_steps.get_nodes(fqdns=[fqdn])
        os_faults_steps.poweron_nodes(node)

    get_nova_client()
    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=tiny_flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    volume = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)


@platform.mcp
@pytest.mark.idempotent_id('7509ac93-f0a3-4b62-84dc-ed722e3eba55')
def test_network_outage(cirros_image,
                        keypair,
                        tiny_flavor,
                        security_group,
                        net_subnet_router,
                        floating_ip,
                        attach_volume_to_server,
                        volume_steps,
                        server_steps,
                        get_nova_client,
                        nova_service_steps,
                        rabbitmq_steps,
                        get_rabbitmq_cluster_data,
                        os_faults_steps):
    """**Scenario:** Check functionality after network outage

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Check Galera state
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

    #. Delete server
    #. Delete volume
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    cluster_node_names, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

    interfaces = os_faults_steps.get_physical_interfaces()
    os_faults_steps.block_interfaces(interfaces, config.NETWORK_OUTAGE_TIME)

    time.sleep(config.NETWORK_OUTAGE_TIME)

    get_nova_client()
    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=tiny_flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    volume = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)


@platform.mcp
@pytest.mark.idempotent_id('8544c689-481c-4c1c-9163-3fad0803813a',
                           os_workload=False)
@pytest.mark.idempotent_id('3cd46899-528e-4c58-9841-2189bb23f7ba',
                           os_workload=True)
@pytest.mark.parametrize('os_workload', [False, True],
                         ids=['without workload', 'with workload'])
def test_reboot_vip_controller(cirros_image,
                               keypair,
                               tiny_flavor,
                               security_group,
                               net_subnet_router,
                               floating_ip,
                               attach_volume_to_server,
                               volume_steps,
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
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Start Openstack workload generation (optional)
    #. Check Galera state
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
    #. Delete server
    #. Delete volume
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    if os_workload:
        generate_os_workload(config.OS_LOAD_GENERATOR)

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    cluster_node_names, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

    vip_controller = os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)

    os_faults_steps.reset_nodes(vip_controller)

    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=tiny_flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    volume = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    _, _, _, cluster_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)


@platform.mcp
@pytest.mark.idempotent_id('ad8f7436-1f00-4132-bbdd-83fc9c4764f9')
def test_graceful_shutdown_cluster(cirros_image,
                                   keypair,
                                   tiny_flavor,
                                   security_group,
                                   net_subnet_router,
                                   floating_ip,
                                   attach_volume_to_server,
                                   volume_steps,
                                   server_steps,
                                   nova_service_steps,
                                   host_steps,
                                   get_rabbitmq_cluster_data,
                                   rabbitmq_steps,
                                   shutdown_nodes,
                                   get_nova_client,
                                   os_faults_steps):
    """**Scenario:** Check functionality after shutdown/start the whole cluster

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Shutdown compute nodes
    #. Shutdown monitoring nodes (if exist)
    #. Shutdown controller nodes
    #. Wait for 5 minutes
    #. Start controller nodes
    #. Wait for nova services work
    #. Start compute nodes
    #. Wait for nova services work
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check Galera state
    #. Check status of RabbitMQ cluster
    #. Start monitoring nodes (if exist)
    #. Check monitoring (if exist): services, alarms and metrics

    **Teardown:**

    #. Delete server
    #. Delete volume
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    controllers = os_faults_steps.get_nodes(service_names=[config.NOVA_API])
    computes = os_faults_steps.get_nodes(service_names=[config.NOVA_COMPUTE])

    stacklight_nodes = {}
    mon_nodes = []
    for service_name in config.STACKLIGHT_SERVICES:
        nodes = os_faults_steps.get_nodes(service_names=[service_name],
                                          check=False)
        if mon_nodes:
            mon_nodes += nodes
        else:
            mon_nodes = nodes
        stacklight_nodes[service_name] = nodes

    controller_host_names = [host_steps.get_host(fqdn=node.fqdn).host_name
                             for node in controllers]

    shutdown_nodes(computes)

    if len(mon_nodes) > 0:
        shutdown_nodes(mon_nodes)

    shutdown_nodes(controllers)

    time.sleep(config.TIME_BETWEEN_CLUSTER_RESTART)

    os_faults_steps.poweron_nodes(controllers)

    get_nova_client()
    nova_service_steps.check_services_up(
        host_names=controller_host_names,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)
    server_steps.get_servers()

    os_faults_steps.poweron_nodes(computes)

    get_nova_client()
    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=tiny_flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    volume = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, floating_ip)
    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    rabbit_node_names, _, _, rabbit_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(rabbit_status, rabbit_node_names)

    if len(mon_nodes) > 0:

        os_faults_steps.poweron_nodes(mon_nodes)
        time.sleep(config.TIME_AFTER_START_MON_NODE)

        for service_name in stacklight_nodes:
            os_faults_steps.check_service_state(
                service_name=service_name,
                nodes=stacklight_nodes[service_name])

        time_start = time.time()
        node = os_faults_steps.get_node(service_names=[config.NOVA_COMPUTE])
        os_faults_steps.terminate_service(config.NOVA_COMPUTE, node)
        time.sleep(config.TIME_BETWEEN_STOP_START_SERVICE)
        os_faults_steps.start_service(config.NOVA_COMPUTE, node)
        time.sleep(config.TIME_BEFORE_ALARM_CHECK)
        os_faults_steps.check_alarms(
            stacklight_nodes[config.INFLUXDB_SERVICE],
            time_start, expected_alarms=[config.TCP_EXPECTED_ALARM])

        os_faults_steps.check_metrics(
            stacklight_nodes[config.INFLUXDB_SERVICE],
            time_start)


@platform.mcp
@pytest.mark.idempotent_id('76a612ca-98ae-4808-b5cc-9a8718991464',
                           os_workload=False)
@pytest.mark.idempotent_id('5814e237-0acd-493b-b97b-8e6d5829a50f',
                           os_workload=True)
@pytest.mark.parametrize('os_workload', [False, True],
                         ids=['without workload', 'with workload'])
def test_stop_rabbitmq(cirros_image,
                       keypair,
                       tiny_flavor,
                       security_group,
                       net_subnet_router,
                       floating_ip,
                       attach_volume_to_server,
                       volume_steps,
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
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

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
    #. Delete server
    #. Delete volume
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    if os_workload:
        generate_os_workload(config.OS_LOAD_GENERATOR)

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    cluster_node_names, fqdns, ip_addresses, cluster_status = (
        get_rabbitmq_cluster_data())
    rabbitmq_steps.check_cluster_status(cluster_status, cluster_node_names)

    disabled_fqdn = fqdns[0]
    disabled_node = os_faults_steps.get_node(fqdns=[disabled_fqdn])
    os_faults_steps.terminate_service(service_name=config.RABBITMQ,
                                      nodes=disabled_node)

    time.sleep(config.TIME_AFTER_RABBITMQ_STOP)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=tiny_flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    volume = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)

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

    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)


@platform.mcp
@pytest.mark.idempotent_id('d445284f-4029-489e-b3d8-2495a4092d28',
                           os_workload=False)
@pytest.mark.idempotent_id('238e32a2-9d85-45fb-8a6b-1b2b26d74fcc',
                           os_workload=True)
@pytest.mark.parametrize('os_workload', [False, True],
                         ids=['without workload', 'with workload'])
def test_unplug_network_on_mysql_node(cirros_image,
                                      keypair,
                                      tiny_flavor,
                                      security_group,
                                      net_subnet_router,
                                      floating_ip,
                                      attach_volume_to_server,
                                      volume_steps,
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
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Start Openstack workload generation (optional)
    #. Check Galera state
    #. Block input/output on MySQL node (not VIP controller) and schedule
    #   its unblock in 4 minutes
    #. Wait for nova services work on available nodes
    #. Check Galera state and data replication on available nodes
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Wait for unblocking input/output on MySQL node
    #. Wait for nova services work on all nodes
    #. Check Galera state

    **Teardown:**

    #. Stop Openstack workload generation (optional)
    #. Delete server
    #. Delete volume
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    if os_workload:
        generate_os_workload(config.OS_LOAD_GENERATOR)

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    nova_nodes = os_faults_steps.get_nodes_with_any_service(
        service_names=[config.NOVA_API, config.NOVA_COMPUTE])

    vip_controller = os_faults_steps.get_nodes_by_cmd(
        config.TCP_VIP_CONTROLLER_CMD)
    mysql_nodes_without_VIP = mysql_nodes - vip_controller
    disabled_node = os_faults_steps.get_node(
        fqdns=[mysql_nodes_without_VIP.hosts[0].fqdn])

    enabled_mysql_nodes = mysql_nodes - disabled_node
    enabled_nova_nodes = nova_nodes - disabled_node
    enabled_host_names = [host_steps.get_host(fqdn=node.fqdn).host_name
                          for node in enabled_nova_nodes]

    os_faults_steps.block_iptables_input_output(
        disabled_node, duration=config.TIME_NETWORK_DOWN)
    network_up_time = time.time() + config.TIME_NETWORK_DOWN

    nova_service_steps.check_services_up(
        host_names=enabled_host_names,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    os_faults_steps.check_galera_cluster_state(
        member_nodes=enabled_mysql_nodes)
    os_faults_steps.check_galera_data_replication(enabled_mysql_nodes)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=tiny_flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    volume = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)

    delay_before_network_up = network_up_time - time.time()
    if delay_before_network_up > 0:
        time.sleep(delay_before_network_up)

    os_faults_steps.reset_nodes(disabled_node)

    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)


@platform.mcp
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
                         tiny_flavor,
                         security_group,
                         net_subnet_router,
                         floating_ip,
                         attach_volume_to_server,
                         volume_steps,
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
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

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
    #. Delete server
    #. Delete volume
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    generate_os_workload(config.OS_LOAD_GENERATOR)

    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

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
                                             flavor=tiny_flavor,
                                             networks=[net_subnet_router[0]],
                                             security_groups=[security_group],
                                             username=config.CIRROS_USERNAME,
                                             password=config.CIRROS_PASSWORD,
                                             keypair=keypair)[0]
        volume = volume_steps.create_volumes()[0]
        attach_volume_to_server(server, volume)

        server_steps.attach_floating_ip(server, floating_ip)

        with server_steps.get_server_ssh(
                server, floating_ip['floating_ip_address']) as server_ssh:
            server_steps.check_ping_for_ip(
                config.GOOGLE_DNS_IP, server_ssh,
                timeout=config.PING_CALL_TIMEOUT)

        os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    time.sleep(config.TIME_AFTER_KEEPALIVED_START)


@platform.mcp
@pytest.mark.idempotent_id('bcb88d70-d347-45fa-9261-71732ac54523')
def test_shutdown_and_bootstrap_galera_cluster(cirros_image,
                                               tiny_flavor,
                                               net_subnet_router,
                                               os_faults_steps,
                                               server_steps):
    """**Scenario:** Check shutdown and bootstrap galera cluster.

    **Setup:**

    #. Create cirros image
    #. Create network, subnet and router

    **Steps:**

    #. Terminate 'mysql' service on all nodes
    #. Run '/usr/bin/mysqld_safe --wsrep-new-cluster' on the one node
    #. Check that new operational cluster is created and its size 1
    #. Add nodes to cluster by start of 'mysql' service
    #. Restart mysql as a service on the primary node
    #. Check that cluster still operational but with new size
    #. Create server to check cluster

    **Teardown:**

    #. Delete server
    #. Delete network, subnet and router
    #. Delete cirros image
    """
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.terminate_service(service_name=config.MYSQL,
                                      nodes=mysql_nodes)

    primary_node = os_faults_steps.get_node(fqdns=[mysql_nodes.hosts[0].fqdn])
    secondary_nodes = mysql_nodes - primary_node

    # Start galera cluster
    os_faults_steps.execute_cmd(primary_node, config.GALERA_CLUSTER_START_CMD)
    time.sleep(config.TIME_AFTER_MYSQL_START)
    os_faults_steps.check_galera_cluster_state(member_nodes=primary_node)

    # Add secondary nodes to cluster
    os_faults_steps.start_service(service_name=config.MYSQL,
                                  nodes=secondary_nodes)
    time.sleep(config.TIME_AFTER_MYSQL_START)

    # Restart mysql as a service on the primary node
    os_faults_steps.execute_cmd(primary_node, config.MYSQL_KILL_CMD)
    os_faults_steps.start_service(service_name=config.MYSQL,
                                  nodes=primary_node)
    time.sleep(config.TIME_AFTER_MYSQL_START)
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    server_steps.create_servers(image=cirros_image,
                                flavor=tiny_flavor,
                                networks=[net_subnet_router[0]])


@platform.mcp
@pytest.mark.idempotent_id('c2b89348-30a6-43b1-b547-9d8615f22e29')
def test_reboot_node_from_galera_cluster_with_load(generate_os_workload,
                                                   cirros_image,
                                                   tiny_flavor,
                                                   net_subnet_router,
                                                   os_faults_steps,
                                                   server_steps):
    """**Scenario:** Check reboot node from galera cluster with workload.

    **Setup:**

    #. Create cirros image
    #. Create network, subnet and router

    **Steps:**

    #. Start Openstack workload generation
    #. Reset one node from Galera cluster
    #. Check that Galera cluster still operational but without rebooted node
    #. Check Galera data replication
    #. Wait for Galera cluster update after node availability
    #. Check cluster state and size
    #. Create server to check cluster operability

    **Teardown:**

    #. Stop Openstack workload generation
    #. Delete server
    #. Delete network, subnet and router
    #. Delete cirros image
    """
    generate_os_workload(config.OS_LOAD_GENERATOR)
    nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    node_to_reboot = os_faults_steps.get_node(fqdns=[nodes.hosts[0].fqdn])
    other_nodes = nodes - node_to_reboot

    os_faults_steps.reset_nodes(node_to_reboot)

    os_faults_steps.check_galera_cluster_state(member_nodes=other_nodes)
    os_faults_steps.check_galera_data_replication(other_nodes)

    time.sleep(config.GALERA_CLUSTER_UP_TIMEOUT)

    os_faults_steps.check_galera_cluster_state(member_nodes=nodes)

    server_steps.create_servers(image=cirros_image,
                                flavor=tiny_flavor,
                                networks=[net_subnet_router[0]])


@platform.mcp
@pytest.mark.idempotent_id('e85c3844-e4ce-48d4-8dd6-0605e65001fb')
def test_fill_root_filesystem_on_vip_controller(server,
                                                server_steps,
                                                get_server_steps,
                                                os_faults_steps,
                                                execute_command_with_rollback):
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

    with execute_command_with_rollback(
            nodes=vip_controller,
            cmd=config.CREATE_FILE_CMD.format(
                size=free_space, file_path=file_path),
            rollback_cmd=config.REMOVE_FILE_CMD.format(file_path=file_path)):
        server_steps.check_servers_actions_not_available(
            timeout=config.GALERA_CLUSTER_DOWN_TIMEOUT)

    server_steps.get_servers()


@platform.mcp
@pytest.mark.requires("kvm_nodes_count > 1")
@pytest.mark.idempotent_id('8c5ca930-d491-416a-84b7-f92461e6f78a')
def test_shutdown_kvm_node(cirros_image,
                           keypair,
                           tiny_flavor,
                           security_group,
                           net_subnet_router,
                           floating_ip,
                           attach_volume_to_server,
                           volume_steps,
                           server_steps,
                           nova_service_steps,
                           host_steps,
                           get_rabbitmq_cluster_data,
                           rabbitmq_steps,
                           shutdown_nodes,
                           os_faults_steps):
    """**Scenario:** Check functionality after shutdown of KVM node

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Check Galera state
    #. Check status of RabbitMQ cluster
    #. Shutdown KVM node
    #. Wait for nova services work
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check Galera state
    #. Check status of RabbitMQ cluster
    #. Check alarms

    **Teardown:**

    #. Power on KVM node
    #. Wait for nova services work
    #. Delete server
    #. Delete volume
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    rabbit_node_names, _, _, rabbit_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(rabbit_status, rabbit_node_names)

    kvm_node = os_faults_steps.get_node_by_cmd(config.TCP_KVM_NODE_CMD)

    shutdown_nodes(kvm_node)
    time.sleep(config.TIME_AFTER_SHUTDOWN_KVM_NODE)

    alive_nova_nodes = os_faults_steps.get_nodes_with_any_service(
        [config.NOVA_API, config.NOVA_COMPUTE])
    alive_nova_host_names = [host_steps.get_host(fqdn=node.fqdn).host_name for
                             node in alive_nova_nodes]

    nova_service_steps.check_services_up(
        host_names=alive_nova_host_names,
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    time_start = time.time()

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=tiny_flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    volume = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    _, _, _, rabbit_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(rabbit_status, rabbit_node_names)

    mon_nodes = os_faults_steps.get_nodes_by_cmd(config.TCP_MON_NODE_CMD)
    if len(mon_nodes) > 0:
        os_faults_steps.check_alarms(mon_nodes, time_start)


@platform.mcp
@pytest.mark.requires("kvm_nodes_count >= 1")
@pytest.mark.idempotent_id('128c1157-d395-4d0c-b01c-d674eeb1238b')
def test_reboot_kvm_node(cirros_image,
                         keypair,
                         tiny_flavor,
                         security_group,
                         net_subnet_router,
                         floating_ip,
                         attach_volume_to_server,
                         volume_steps,
                         server_steps,
                         nova_service_steps,
                         get_rabbitmq_cluster_data,
                         rabbitmq_steps,
                         os_faults_steps):
    """**Scenario:** Check functionality after reboot of KVM node

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Check Galera state
    #. Check status of RabbitMQ cluster
    #. Reboot KVM node
    #. Wait for nova services work
    #. Create server with volume
    #. Attach floating IP
    #. Check connectivity from server
    #. Check Galera state
    #. Check status of RabbitMQ cluster
    #. Check alarms

    **Teardown:**

    #. Delete server
    #. Delete volume
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    """
    mysql_nodes = os_faults_steps.get_nodes(service_names=[config.MYSQL])
    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    rabbit_node_names, _, _, rabbit_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(rabbit_status, rabbit_node_names)

    kvm_node = os_faults_steps.get_node_by_cmd(config.TCP_KVM_NODE_CMD)

    os_faults_steps.reset_nodes(kvm_node)

    os_faults_steps.check_all_nodes_availability(
        timeout=config.NODES_ON_KVM_START_TIMEOUT)

    nova_service_steps.check_services_up(
        timeout=config.NOVA_SERVICES_UP_TIMEOUT)
    time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)

    time_start = time.time()

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=tiny_flavor,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME,
                                         password=config.CIRROS_PASSWORD,
                                         keypair=keypair)[0]
    volume = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume)

    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.check_galera_cluster_state(member_nodes=mysql_nodes)

    _, _, _, rabbit_status = get_rabbitmq_cluster_data()
    rabbitmq_steps.check_cluster_status(rabbit_status, rabbit_node_names)

    mon_nodes = os_faults_steps.get_nodes_by_cmd(config.TCP_MON_NODE_CMD)
    if len(mon_nodes) > 0:
        os_faults_steps.check_alarms(mon_nodes, time_start)
