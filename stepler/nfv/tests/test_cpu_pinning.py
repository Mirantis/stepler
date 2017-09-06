"""
---------------------
NFV CPU pinning tests
---------------------
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

from novaclient import exceptions as nova_exceptions
import pytest

from stepler import config
from stepler.third_party import utils

pytestmark = pytest.mark.requires("vlan")


@pytest.mark.requires("cpu_pinning_computes_count >= 3")
@pytest.mark.idempotent_id('e75b8e86-de24-4aa4-8341-ada01870e3ad')
def test_cpu_pinning_diff_modes(create_aggregate,
                                aggregate_steps,
                                cirros_image,
                                keypair,
                                create_flavor,
                                flavor_steps,
                                security_group,
                                neutron_2_networks,
                                create_floating_ip,
                                server_steps,
                                host_steps,
                                nfv_steps,
                                os_faults_steps):
    """**Scenario:** Check server creation with different modes of cpu pinning.

    **Setup:**

    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create two networks, subnets and one router

    **Steps:**

    #. Create aggregate1 with pinned=True and host1 and host2
    #. Create aggregate2 with pinned=False and host3
    #. Get current CPU distribution for 3 hosts
    #. Create flavor1 (pinned=True, numa_nodes=1)
    #. Create flavor2 (pinned=False, numa_nodes=1)
    #. Create server1 on host1, network1, flavor1
    #. Create server2 on host2, network2, flavor2
    #. Create server3 on host3, network1, flavor1
    #. Create and attach floating IPs to servers
    #. Check CPU allocation for server1 and server3
    #. Check connectivity between servers

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavors
    #. Delete keypair
    #. Delete cirros image
    #. Delete aggregates
    """
    aggregate_1 = create_aggregate()
    metadata = {'pinned': 'true'}
    aggregate_steps.set_metadata(aggregate_1, metadata)

    aggregate_2 = create_aggregate()
    metadata = {'pinned': 'false'}
    aggregate_steps.set_metadata(aggregate_2, metadata)

    host_names = []
    computes = os_faults_steps.get_cpu_pinning_computes()
    for compute in computes:
        host = host_steps.get_host(fqdn=compute.fqdn)
        if len(aggregate_1.hosts) < 2:
            aggregate_steps.add_host(aggregate_1, host.host_name)
        else:
            aggregate_steps.add_host(aggregate_2, host.host_name)
        host_names.append(host.host_name)

    host_cpus = []
    for host_name in host_names[:3]:
        fqdn = os_faults_steps.get_fqdn_by_host_name(host_name)
        node = os_faults_steps.get_nodes(fqdns=[fqdn])
        host_cpus.append(
            os_faults_steps.get_cpu_distribition_per_numa_node(node))

    flavor_name = next(utils.generate_ids('flavor'))
    flavor_1 = create_flavor(flavor_name, ram=2048, vcpus=2, disk=20)
    metadata = {'hw:cpu_policy': 'dedicated',
                'aggregate_instance_extra_specs:pinned': 'true',
                'hw:numa_nodes': '1'}
    flavor_steps.set_metadata(flavor_1, metadata)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor_2 = create_flavor(flavor_name, ram=2048, vcpus=2, disk=20)
    metadata = {'aggregate_instance_extra_specs:pinned': 'false'}
    flavor_steps.set_metadata(flavor_2, metadata)

    flavors = [flavor_1, flavor_2, flavor_1]

    networks = [neutron_2_networks.networks[0],
                neutron_2_networks.networks[1],
                neutron_2_networks.networks[0]]

    servers = []
    for i in range(3):
        server = server_steps.create_servers(
            image=cirros_image,
            flavor=flavors[i],
            networks=[networks[i]],
            security_groups=[security_group],
            username=config.CIRROS_USERNAME,
            password=config.CIRROS_PASSWORD,
            keypair=keypair,
            availability_zone='nova:{}'.format(host_names[i]))[0]
        floating_ip = create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)
        servers.append(server)

    for i in [0, 2]:
        server_dump = os_faults_steps.get_server_dump(servers[i])
        nfv_steps.check_cpu_for_server(server_dump, 1, host_cpus[i])

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("cpu_pinning_computes_count >= 2")
@pytest.mark.idempotent_id('e46620e6-0383-4d40-9d0b-f9085f62621f')
def test_cpu_pinning_resize(pinned_aggregate,
                            cirros_image,
                            keypair,
                            create_flavor,
                            flavor_steps,
                            security_group,
                            neutron_2_networks,
                            create_floating_ip,
                            server_steps,
                            nfv_steps,
                            os_faults_steps):
    """**Scenario:** Check resize of server on host with cpu pinning.

    **Setup:**

    #. Create aggregate with pinned=True and hosts with CPU pinning
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create two networks, subnets and one router

    **Steps:**

    #. Get current CPU distribution
    #. Create flavors: | pinned | numa_nodes | ram  | vcpus | disk:
    #                1 |  true  |   1        | 512  |  1    |  1
    #                2 |  false |            | 2048 |  2    |  1
    #                3 |  true  |   2        | 512  |  2    |  1
    #                4 |  true  |   2        | 2000 |  4    |  1
    #                5 |  true  |   1        | 512  |  2    |  1
    #. Create server1 with flavor1 on compute1
    #. Create server2 with flavor2 on compute2
    #. Create and attach floating IPs to both servers
    #. Resize server1 to flavors 2, 3, 0, 1, 4, 0
    #. For each resize:
    #.     - check CPU allocation
    #.     - check connectivity between servers

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavors
    #. Delete keypair
    #. Delete cirros image
    #. Delete aggregate
    """
    host_names = []
    for i in range(2):
        host_names.append(pinned_aggregate.hosts[i])
    fqdn = os_faults_steps.get_fqdn_by_host_name(host_names[0])
    node = os_faults_steps.get_nodes(fqdns=[fqdn])
    host_cpus = os_faults_steps.get_cpu_distribition_per_numa_node(node)

    flavors = []
    for numa_count, ram, vcpus in (
            (1, 512, 1),
            (0, 2048, 2),
            (2, 512, 2),
            (2, 2000, 4),
            (1, 512, 2)):
        flavor_name = next(utils.generate_ids('flavor'))
        flavor = create_flavor(flavor_name, ram=ram, vcpus=vcpus, disk=1)
        if numa_count == 0:
            metadata = {'aggregate_instance_extra_specs:pinned': 'false'}
        else:
            metadata = {'hw:cpu_policy': 'dedicated',
                        'aggregate_instance_extra_specs:pinned': 'true',
                        'hw:numa_nodes': str(numa_count)}
        flavor_steps.set_metadata(flavor, metadata)
        flavors.append(flavor)

    servers = []
    for i in range(2):
        server = server_steps.create_servers(
            image=cirros_image,
            flavor=flavors[i],
            networks=[neutron_2_networks.networks[i]],
            security_groups=[security_group],
            username=config.CIRROS_USERNAME,
            password=config.CIRROS_PASSWORD,
            keypair=keypair,
            availability_zone='nova:{}'.format(host_names[i]))[0]
        floating_ip = create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)
        servers.append(server)

    for flavor_i in (2, 3, 0, 1, 4, 0):
        server_steps.resize(servers[0], flavors[flavor_i])
        server_steps.confirm_resize_servers([servers[0]])

        server_dump = os_faults_steps.get_server_dump(servers[0])
        numa_count = int(flavor_steps.get_metadata(flavors[flavor_i]).get(
            'hw:numa_nodes', 0))
        nfv_steps.check_cpu_for_server(server_dump, numa_count, host_cpus)

        server_steps.check_ping_between_servers_via_floating(
            servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("cpu_pinning_computes_count >= 2")
@pytest.mark.idempotent_id('0e0bcfdb-0294-4b71-83ab-6c42b5571ee9')
def test_cpu_pinning_migrate(pinned_aggregate,
                             cirros_image,
                             keypair,
                             create_flavor,
                             flavor_steps,
                             security_group,
                             neutron_2_networks,
                             create_floating_ip,
                             server_steps,
                             nfv_steps,
                             os_faults_steps):
    """**Scenario:** Check migration of server on hosts with cpu pinning.

    **Setup:**

    #. Create aggregate with pinned=True and hosts with CPU pinning
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create two networks, subnets and one router

    **Steps:**

    #. Get current CPU distribution
    #. Create flavor (pinned=True, numa_nodes=2)
    #. Create server1 on compute1
    #. Create server2 on compute2
    #. Create and attach floating IPs to both servers
    #. Migrate server1 to another host
    #. Check CPU allocation
    #. Check connectivity between servers

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavors
    #. Delete keypair
    #. Delete cirros image
    #. Delete aggregate
    """
    host_names = []
    for i in range(2):
        host_names.append(pinned_aggregate.hosts[i])
    fqdn = os_faults_steps.get_fqdn_by_host_name(host_names[0])
    node = os_faults_steps.get_nodes(fqdns=[fqdn])
    host_cpus = os_faults_steps.get_cpu_distribition_per_numa_node(node)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=2048, vcpus=2, disk=20)
    metadata = {'hw:cpu_policy': 'dedicated',
                'aggregate_instance_extra_specs:pinned': 'true',
                'hw:numa_nodes': '2'}
    flavor_steps.set_metadata(flavor, metadata)

    servers = []
    for i in range(2):
        server = server_steps.create_servers(
            image=cirros_image,
            flavor=flavor,
            networks=[neutron_2_networks.networks[i]],
            security_groups=[security_group],
            username=config.CIRROS_USERNAME,
            password=config.CIRROS_PASSWORD,
            keypair=keypair,
            availability_zone='nova:{}'.format(host_names[i]))[0]
        floating_ip = create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)
        servers.append(server)

    server_steps.migrate_servers([servers[0]])
    server_steps.confirm_resize_servers([servers[0]])

    server_dump = os_faults_steps.get_server_dump(servers[0])
    nfv_steps.check_cpu_for_server(server_dump, 2, host_cpus)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("cpu_pinning_computes_count >= 1")
@pytest.mark.idempotent_id('bb59d87d-1390-401a-bfc7-6134ff049e19')
def test_cpu_and_memory_distribution(pinned_aggregate,
                                     cirros_image,
                                     keypair,
                                     create_flavor,
                                     flavor_steps,
                                     security_group,
                                     net_subnet_router,
                                     floating_ip,
                                     server_steps,
                                     nfv_steps,
                                     os_faults_steps):
    """**Scenario:** Check distribution of cpu and memory for server.

    **Setup:**

    #. Create aggregate with pinned=True and hosts with CPU pinning
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Get current CPU distribution
    #. Create flavor with custom numa_cpu and numa_mem distribution
    #. Create server
    #. Check CPU and memory allocation per numa node
    #. Attach floating IP
    #. Check connectivity from server

    **Teardown:**

    #. Delete server
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    #. Delete aggregate
    """
    host_name = pinned_aggregate.hosts[0]
    fqdn = os_faults_steps.get_fqdn_by_host_name(host_name)
    node = os_faults_steps.get_nodes(fqdns=[fqdn])
    host_cpus = os_faults_steps.get_cpu_distribition_per_numa_node(node)
    host_mem = os_faults_steps.get_memory_distribition_per_numa_node(node)

    vcpus, ram, cpu_numa0, cpu_numa1, mem_numa0, mem_numa1 = (
        nfv_steps.get_cpu_mem_numa_values(
            host_cpus, host_mem, case='normal'))

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=ram, vcpus=vcpus, disk=1)
    metadata = {'hw:cpu_policy': 'dedicated',
                'aggregate_instance_extra_specs:pinned': 'true',
                'hw:numa_nodes': '2',
                'hw:numa_cpus.0': cpu_numa0,
                'hw:numa_cpus.1': cpu_numa1,
                'hw:numa_mem.0': str(mem_numa0),
                'hw:numa_mem.1': str(mem_numa1)}
    flavor_steps.set_metadata(flavor, metadata)

    numa_count = 2
    exp_mem = {'0': mem_numa0, '1': mem_numa1}
    exp_pin = {
        'numa0': [int(cpu) for cpu in cpu_numa0.split(',')],
        'numa1': [int(cpu) for cpu in cpu_numa1.split(',')]}

    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD,
        keypair=keypair,
        availability_zone='nova:{}'.format(host_name))[0]

    server_dump = os_faults_steps.get_server_dump(server)
    nfv_steps.check_cpu_for_server(server_dump, numa_count, host_cpus, exp_pin)
    nfv_steps.check_memory_allocation(server_dump, numa_count, exp_mem)

    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.requires("cpu_pinning_computes_count >= 1")
@pytest.mark.idempotent_id('9b57d4c7-1505-41a0-93ed-7dbdeae025da')
def test_negative_distribution_one_numa(pinned_aggregate,
                                        cirros_image,
                                        keypair,
                                        create_flavor,
                                        flavor_steps,
                                        security_group,
                                        net_subnet_router,
                                        server_steps,
                                        nfv_steps,
                                        os_faults_steps):
    """**Scenario:** Check server creation with wrong flavor metadata.

    Flavor metadata contains one numa node, but CPU and memory for two nodes:
    hw:cpu_policy=dedicated
    aggregate_instance_extra_specs:pinned=true
    hw:numa_nodes=1
    hw:numa_cpus.0=0,2,3
    hw:numa_cpus.1=1
    hw:numa_mem.0=512
    hw:numa_mem.1=1536

    **Setup:**

    #. Create aggregate with pinned=True and hosts with CPU pinning
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router

    **Steps:**

    #. Get current CPU distribution
    #. Create flavor with wrong metadata
    #. Try to create server

    **Teardown:**

    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    #. Delete aggregate
    """
    host_name = pinned_aggregate.hosts[0]
    fqdn = os_faults_steps.get_fqdn_by_host_name(host_name)
    node = os_faults_steps.get_nodes(fqdns=[fqdn])
    host_cpus = os_faults_steps.get_cpu_distribition_per_numa_node(node)
    host_mem = os_faults_steps.get_memory_distribition_per_numa_node(node)

    vcpus, ram, cpu_numa0, cpu_numa1, mem_numa0, mem_numa1 = (
        nfv_steps.get_cpu_mem_numa_values(
            host_cpus, host_mem, case='normal'))

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=ram, vcpus=vcpus, disk=1)
    metadata = {'hw:cpu_policy': 'dedicated',
                'aggregate_instance_extra_specs:pinned': 'true',
                'hw:numa_nodes': '1',
                'hw:numa_cpus.0': cpu_numa0,
                'hw:numa_cpus.1': cpu_numa1,
                'hw:numa_mem.0': str(mem_numa0),
                'hw:numa_mem.1': str(mem_numa1)}
    flavor_steps.set_metadata(flavor, metadata)

    server_steps.check_create_server_negative(
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        security_groups=[security_group],
        keypair=keypair,
        availability_zone='nova:{}'.format(host_name),
        exp_exception=nova_exceptions.BadRequest)


@pytest.mark.requires("cpu_pinning_computes_count >= 1")
@pytest.mark.idempotent_id('6b0a5479-b65b-4518-b452-08d0280a6d51',
                           resource='ram')
@pytest.mark.idempotent_id('cb6e5bc2-f8d6-4761-8b58-27488368cdc6',
                           resource='cpu')
@pytest.mark.parametrize('resource', ['ram', 'cpu'])
def test_negative_distribution_less_resources(pinned_aggregate,
                                              cirros_image,
                                              keypair,
                                              create_flavor,
                                              flavor_steps,
                                              security_group,
                                              net_subnet_router,
                                              server_steps,
                                              nfv_steps,
                                              os_faults_steps,
                                              resource):
    """**Scenario:** Check server creation with wrong flavor metadata.

    Flavor metadata contains inconsistent resource values:
    for RAM:
        hw:cpu_policy=dedicated
        aggregate_instance_extra_specs:pinned=true
        hw:numa_nodes=2
        hw:numa_cpus.0=0,1 (depends on current CPU values)
        hw:numa_cpus.1=2,3 (depends on current CPU values)
        hw:numa_mem.0=<More than we have on NUMA node>
        hw:numa_mem.1=<Less than we have on another NUMA node>
    for CPU:
        hw:cpu_policy=dedicated
        aggregate_instance_extra_specs:pinned=true
        hw:numa_nodes=2
        hw:numa_cpus.0=<more than available>
        hw:numa_cpus.1=<less than available>
        hw:numa_mem.0=1024 (depends on current RAM values)
        hw:numa_mem.1=1024 (depends on current RAM values)

    **Setup:**

    #. Create aggregate with pinned=True and hosts with CPU pinning
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router

    **Steps:**

    #. Get current CPU and RAM distribution
    #. Create flavor with wrong metadata
    #. Try to create server and check error

    **Teardown:**

    #. Delete server (if exist)
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    #. Delete aggregate
    """
    host_name = pinned_aggregate.hosts[0]
    fqdn = os_faults_steps.get_fqdn_by_host_name(host_name)
    node = os_faults_steps.get_nodes(fqdns=[fqdn])
    host_cpus = os_faults_steps.get_cpu_distribition_per_numa_node(node)
    host_mem = os_faults_steps.get_memory_distribition_per_numa_node(node)

    vcpus, ram, cpu_numa0, cpu_numa1, mem_numa0, mem_numa1 = (
        nfv_steps.get_cpu_mem_numa_values(
            host_cpus, host_mem, case='wrong_{}'.format(resource)))

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=ram, vcpus=vcpus, disk=1)
    metadata = {'hw:cpu_policy': 'dedicated',
                'aggregate_instance_extra_specs:pinned': 'true',
                'hw:numa_nodes': '2',
                'hw:numa_cpus.0': cpu_numa0,
                'hw:numa_cpus.1': cpu_numa1,
                'hw:numa_mem.0': str(mem_numa0),
                'hw:numa_mem.1': str(mem_numa1)}
    flavor_steps.set_metadata(flavor, metadata)

    server_steps.check_create_server_negative(
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        security_groups=[security_group],
        keypair=keypair,
        availability_zone='nova:{}'.format(host_name),
        exp_error_message=config.CANNOT_FIT_NUMA_TOPOLOGY)
