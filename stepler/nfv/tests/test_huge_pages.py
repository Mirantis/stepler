"""
--------------------
NFV huge pages tests
--------------------
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

import time

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.requires("vlan")
@pytest.mark.parametrize('computes_with_hp_2mb',
                         [{'host_count': 2, 'hp_count_per_host': 1024}],
                         indirect=['computes_with_hp_2mb'])
@pytest.mark.idempotent_id('df9c0279-92cd-44ed-8f80-791121b57f7f')
def test_allocation_huge_pages_2mb(computes_with_hp_2mb,
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
    """**Scenario:** Check allocation of 2Mb HugePages for servers

    **Setup:**

    #. Find two computes with HP 2Mb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create two networks, subnets and one router

    **Steps:**

    #. Get current HP total and free values on computes
    #. Create flavor with mem_page_size=2048
    #. Create server1 and server2 on host1, network1
    #. Create server3 on host1, network2
    #. Create server4 on host2, network2
    #. Create and attach floating IPs to servers
    #. Check HP sizes of all servers using dumps
    #. Check current HP total and free values on computes
    #. Check connectivity between servers

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    fqdns_2mb = computes_with_hp_2mb
    host_names_2mb = [host_steps.get_host(fqdn=fqdn).host_name
                      for fqdn in fqdns_2mb]

    computes_hp_data = os_faults_steps.get_hugepages_data(
        sizes=[config.page_2mb])

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=512, vcpus=1, disk=1)
    metadata = {'hw:mem_page_size': str(config.page_2mb)}
    flavor_steps.set_metadata(flavor, metadata)

    networks = [neutron_2_networks.networks[0],
                neutron_2_networks.networks[0],
                neutron_2_networks.networks[1],
                neutron_2_networks.networks[1]]

    host_names = [host_names_2mb[0],
                  host_names_2mb[0],
                  host_names_2mb[0],
                  host_names_2mb[1]]

    servers = []
    for i in range(4):
        server = server_steps.create_servers(
            image=cirros_image,
            flavor=flavor,
            networks=[networks[i]],
            security_groups=[security_group],
            username=config.CIRROS_USERNAME,
            password=config.CIRROS_PASSWORD,
            keypair=keypair,
            availability_zone='nova:{}'.format(host_names[i]))[0]
        floating_ip = create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)
        servers.append(server)

    for server in servers:
        server_dump = os_faults_steps.get_server_dump(server)
        nfv_steps.check_server_page_size(server_dump, [config.page_2mb])

    computes_hp_data_new = os_faults_steps.get_hugepages_data(
        sizes=[config.page_2mb])

    count_to_allocate_2mb = flavor.ram * 1024 / config.page_2mb
    diff_hps = {fqdns_2mb[0]: {config.page_2mb: 3 * count_to_allocate_2mb},
                fqdns_2mb[1]: {config.page_2mb: 1 * count_to_allocate_2mb}}
    nfv_steps.check_hugepage_diff(computes_hp_data,
                                  computes_hp_data_new,
                                  diff_hps)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("vlan")
@pytest.mark.parametrize('computes_with_hp_mixed',
                         [{'host_count': 2, 'hp_count_2mb': 512,
                           'hp_count_1gb': 4}],
                         indirect=['computes_with_hp_mixed'])
@pytest.mark.idempotent_id('fd7b9705-26f2-4073-82ff-5f17b6554b72')
def test_allocation_huge_pages_2mb_1gb(computes_with_hp_mixed,
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
    """**Scenario:** Check allocation of 2Mb and 1Gb HugePages for servers

    **Setup:**

    #. Find two computes with HP 2Mb and 1Gb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create two networks, subnets and one router

    **Steps:**

    #. Get current HP total and free values on computes
    #. Create flavor1 with mem_page_size=2048
    #. Create flavor2 with mem_page_size=1048576
    #. Create server1 with flavor1 on host1, network1
    #. Create server2 with flavor2 on host2, network2
    #. Create server3 with flavor2 on host1, network2
    #. Create and attach floating IPs to servers
    #. Check HP sizes of all servers using dumps
    #. Check current HP total and free values on computes
    #. Check connectivity between servers

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavors
    #. Delete keypair
    #. Delete cirros image
    """
    fqdns_mixed = computes_with_hp_mixed
    host_names_mixed = [host_steps.get_host(fqdn=fqdn).host_name
                        for fqdn in fqdns_mixed]

    computes_hp_data = os_faults_steps.get_hugepages_data()

    flavor_name = next(utils.generate_ids('flavor'))
    flavor_2mb = create_flavor(flavor_name, ram=512, vcpus=1, disk=1)
    metadata = {'hw:mem_page_size': str(config.page_2mb)}
    flavor_steps.set_metadata(flavor_2mb, metadata)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor_1gb = create_flavor(flavor_name, ram=2048, vcpus=2, disk=20)
    metadata = {'hw:mem_page_size': str(config.page_1gb)}
    flavor_steps.set_metadata(flavor_1gb, metadata)

    flavors = [flavor_2mb, flavor_1gb, flavor_1gb]
    exp_sizes = [config.page_2mb, config.page_1gb, config.page_1gb]

    networks = [neutron_2_networks.networks[0],
                neutron_2_networks.networks[1],
                neutron_2_networks.networks[1]]

    host_names = [host_names_mixed[0],
                  host_names_mixed[1],
                  host_names_mixed[0]]

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

    for i in range(3):
        server_dump = os_faults_steps.get_server_dump(servers[i])
        nfv_steps.check_server_page_size(server_dump, [exp_sizes[i]])

    computes_hp_data_new = os_faults_steps.get_hugepages_data()

    count_to_allocate_2mb = flavor_2mb.ram * 1024 / config.page_2mb
    count_to_allocate_1gb = flavor_1gb.ram * 1024 / config.page_1gb
    diff_hps = {fqdns_mixed[0]: {config.page_2mb: 1 * count_to_allocate_2mb,
                                 config.page_1gb: 1 * count_to_allocate_1gb},
                fqdns_mixed[1]: {config.page_1gb: 1 * count_to_allocate_1gb}}
    nfv_steps.check_hugepage_diff(computes_hp_data,
                                  computes_hp_data_new,
                                  diff_hps)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("vlan")
@pytest.mark.requires("computes_count >= 3")
@pytest.mark.parametrize('computes_with_hp_2mb',
                         [{'host_count': 2, 'hp_count_per_host': 512}],
                         indirect=['computes_with_hp_2mb'])
@pytest.mark.idempotent_id('35ca47bf-7b41-4ce0-bb74-7ecc01b8586b')
def test_migration_huge_pages_2mb(computes_with_hp_2mb,
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
    """**Scenario:** Check cold migration of server with 2Mb HugePages

    **Setup:**

    #. Find two computes with HP 2Mb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create two networks, subnets and one router

    **Steps:**

    #. Get current HP total and free values on computes
    #. Create flavor with mem_page_size=2048
    #. Create server1 and server2 on different networks
    #. Create and attach floating IPs to servers
    #. Check that servers are hosted on computes with HP
    #. Check HP sizes of all servers using dumps
    #. Check current HP total and free values on computes
    #. Check connectivity between servers
    #. Migrate server1
    #. Check that server1 is hosted on compute with HP
    #. Check HP size of server1 using dump
    #. Check current HP total and free values on computes
    #. Check connectivity between servers

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    fqdns_2mb = computes_with_hp_2mb
    host_names_2mb = [host_steps.get_host(fqdn=fqdn).host_name
                      for fqdn in fqdns_2mb]

    computes_hp_data = os_faults_steps.get_hugepages_data(
        sizes=[config.page_2mb])

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=512, vcpus=1, disk=1)
    metadata = {'hw:mem_page_size': str(config.page_2mb)}
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
            keypair=keypair)[0]
        floating_ip = create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)
        servers.append(server)

    for server in servers:
        server_steps.check_server_host_attr(server, host_names=host_names_2mb)

    for server in servers:
        server_dump = os_faults_steps.get_server_dump(server)
        nfv_steps.check_server_page_size(server_dump, [config.page_2mb])

    count_to_allocate_2mb = flavor.ram * 1024 / config.page_2mb

    diff_hps = {fqdn: {config.page_2mb: 0} for fqdn in fqdns_2mb}
    for i in range(2):
        host_name = getattr(servers[i], config.SERVER_ATTR_HOST)
        fqdn = os_faults_steps.get_fqdn_by_host_name(host_name)
        diff_hps[fqdn][config.page_2mb] += count_to_allocate_2mb
        if i == 0:
            old_fqdn = fqdn

    computes_hp_data_after_creation = os_faults_steps.get_hugepages_data(
        sizes=[config.page_2mb])

    nfv_steps.check_hugepage_diff(computes_hp_data,
                                  computes_hp_data_after_creation,
                                  diff_hps)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    server_steps.migrate_servers([servers[0]])
    server_steps.confirm_resize_servers([servers[0]])

    server_steps.check_server_host_attr(servers[0], host_names=host_names_2mb)

    server_dump = os_faults_steps.get_server_dump(servers[0])
    nfv_steps.check_server_page_size(server_dump, [config.page_2mb])

    new_host = getattr(servers[0], config.SERVER_ATTR_HOST)
    new_fqdn = os_faults_steps.get_fqdn_by_host_name(new_host)

    diff_hps[old_fqdn][config.page_2mb] -= count_to_allocate_2mb
    diff_hps[new_fqdn][config.page_2mb] += count_to_allocate_2mb

    computes_hp_data_after_migration = os_faults_steps.get_hugepages_data(
        sizes=[config.page_2mb])

    nfv_steps.check_hugepage_diff(computes_hp_data,
                                  computes_hp_data_after_migration,
                                  diff_hps)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("vlan")
@pytest.mark.requires("computes_count >= 3")
@pytest.mark.parametrize('computes_with_hp_1gb',
                         [{'host_count': 2, 'hp_count_per_host': 4}],
                         indirect=['computes_with_hp_1gb'])
@pytest.mark.idempotent_id('bff8064a-7369-415b-9862-cce6f7e640d6')
def test_migration_huge_pages_1gb(computes_with_hp_1gb,
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
    """**Scenario:** Check cold migration of server with 1Gb HugePages

    **Setup:**

    #. Find two computes with HP 1Gb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create two networks, subnets and one router

    **Steps:**

    #. Get current HP total and free values on computes
    #. Create flavor with mem_page_size=1048576
    #. Create server1 and server2 on different networks
    #. Create and attach floating IPs to servers
    #. Check that servers are hosted on computes with HP
    #. Check HP sizes of all servers using dumps
    #. Check current HP total and free values on computes
    #. Check connectivity between servers
    #. Migrate server1
    #. Check that server1 is hosted on compute with HP
    #. Check HP size of server1 using dump
    #. Check current HP total and free values on computes
    #. Check connectivity between servers

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    fqdns_1gb = computes_with_hp_1gb
    host_names_1gb = [host_steps.get_host(fqdn=fqdn).host_name
                      for fqdn in fqdns_1gb]

    computes_hp_data = os_faults_steps.get_hugepages_data(
        sizes=[config.page_1gb])

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=2048, vcpus=2, disk=20)
    metadata = {'hw:mem_page_size': str(config.page_1gb)}
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
            keypair=keypair)[0]
        floating_ip = create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)
        servers.append(server)

    for server in servers:
        server_steps.check_server_host_attr(server, host_names=host_names_1gb)

    for server in servers:
        server_dump = os_faults_steps.get_server_dump(server)
        nfv_steps.check_server_page_size(server_dump, [config.page_1gb])

    count_to_allocate_1gb = flavor.ram * 1024 / config.page_1gb

    diff_hps = {fqdn: {config.page_1gb: 0} for fqdn in fqdns_1gb}
    for i in range(2):
        host_name = getattr(servers[i], config.SERVER_ATTR_HOST)
        fqdn = os_faults_steps.get_fqdn_by_host_name(host_name)
        diff_hps[fqdn][config.page_1gb] += count_to_allocate_1gb
        if i == 0:
            old_fqdn = fqdn

    computes_hp_data_after_creation = os_faults_steps.get_hugepages_data(
        sizes=[config.page_1gb])

    nfv_steps.check_hugepage_diff(computes_hp_data,
                                  computes_hp_data_after_creation,
                                  diff_hps)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    server_steps.migrate_servers([servers[0]])
    server_steps.confirm_resize_servers([servers[0]])

    server_steps.check_server_host_attr(servers[0], host_names=host_names_1gb)

    server_dump = os_faults_steps.get_server_dump(servers[0])
    nfv_steps.check_server_page_size(server_dump, [config.page_1gb])

    new_host = getattr(servers[0], config.SERVER_ATTR_HOST)
    new_fqdn = os_faults_steps.get_fqdn_by_host_name(new_host)

    diff_hps[old_fqdn][config.page_1gb] -= count_to_allocate_1gb
    diff_hps[new_fqdn][config.page_1gb] += count_to_allocate_1gb

    computes_hp_data_after_migration = os_faults_steps.get_hugepages_data(
        sizes=[config.page_1gb])

    nfv_steps.check_hugepage_diff(computes_hp_data,
                                  computes_hp_data_after_migration,
                                  diff_hps)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("vlan")
@pytest.mark.requires("computes_count >= 2")
@pytest.mark.parametrize('computes_with_hp_2mb',
                         [{'host_count': 2, 'hp_count_per_host': 1024}],
                         indirect=['computes_with_hp_2mb'])
@pytest.mark.idempotent_id('6ea65424-4ad2-48c6-9dda-0e0da396c97e')
def test_evacuation_huge_pages_2mb(computes_with_hp_2mb,
                                   nova_api_node,
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
    """**Scenario:** Check server evacuation with 2Mb HugePages

    **Setup:**

    #. Find two computes with HP 2Mb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create two networks, subnets and one router

    **Steps:**

    #. Get current HP total and free values on computes
    #. Create flavor with mem_page_size=2048
    #. Create server1 on host1, network1
    #. Create server2 on host2, network2
    #. Create and attach floating IPs to servers
    #. Check HP sizes of all servers using dumps
    #. Check current HP total and free values on computes
    #. Check connectivity between servers
    #. Stop nova-compute on host1 and force service to down
    #. Evacuate server1
    #. Unset force service to down and start nova-compute on host1
    #. Check HP sizes of servers using dumps
    #. Check current HP total and free values on computes
    #. Check connectivity between servers

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    fqdns_2mb = computes_with_hp_2mb
    host_names_2mb = [host_steps.get_host(fqdn=fqdn).host_name
                      for fqdn in fqdns_2mb]

    computes_hp_data = os_faults_steps.get_hugepages_data(
        sizes=[config.page_2mb])

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=512, vcpus=1, disk=1)
    metadata = {'hw:mem_page_size': '2048'}
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
            availability_zone='nova:{}'.format(host_names_2mb[i]))[0]
        floating_ip = create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)
        servers.append(server)

    for server in servers:
        server_dump = os_faults_steps.get_server_dump(server)
        nfv_steps.check_server_page_size(server_dump, [config.page_2mb])

    computes_hp_data_new = os_faults_steps.get_hugepages_data(
        sizes=[config.page_2mb])

    count_to_allocate_2mb = flavor.ram * 1024 / config.page_2mb
    diff_hps = {fqdn: {config.page_2mb: 0} for fqdn in fqdns_2mb}
    diff_hps[fqdns_2mb[0]][config.page_2mb] = count_to_allocate_2mb
    diff_hps[fqdns_2mb[1]][config.page_2mb] = count_to_allocate_2mb
    nfv_steps.check_hugepage_diff(computes_hp_data,
                                  computes_hp_data_new,
                                  diff_hps)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    failed_compute = os_faults_steps.get_node(fqdns=[fqdns_2mb[0]])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute)
    os_faults_steps.nova_compute_force_down(nova_api_node, host_names_2mb[0])

    server_steps.evacuate_servers([servers[0]])

    os_faults_steps.nova_compute_force_down(nova_api_node, host_names_2mb[0],
                                            unset=True)
    os_faults_steps.start_service(config.NOVA_COMPUTE, nodes=failed_compute)

    time.sleep(config.TIME_AFTER_NOVA_COMPUTE_UP)

    for server in servers:
        server_dump = os_faults_steps.get_server_dump(server)
        nfv_steps.check_server_page_size(server_dump, [config.page_2mb])

    new_host = getattr(servers[0], config.SERVER_ATTR_HOST)
    new_fqdn = os_faults_steps.get_fqdn_by_host_name(new_host)

    diff_hps[fqdns_2mb[0]][config.page_2mb] -= count_to_allocate_2mb
    diff_hps[new_fqdn][config.page_2mb] += count_to_allocate_2mb

    computes_hp_data_after_evacuation = os_faults_steps.get_hugepages_data(
        sizes=[config.page_2mb])

    nfv_steps.check_hugepage_diff(computes_hp_data,
                                  computes_hp_data_after_evacuation,
                                  diff_hps)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.parametrize('computes_with_hp_mixed',
                         [{'host_count': 1, 'hp_count_2mb': 2048,
                           'hp_count_1gb': 4}],
                         indirect=['computes_with_hp_mixed'])
@pytest.mark.parametrize('mem_page_size, page_sizes',
                         [('large', [config.page_1gb]),
                          ('any', [config.page_2mb, config.page_1gb])],
                         ids=['large', 'any'])
@pytest.mark.idempotent_id('431f7fa3-f060-420e-a2cb-1aac10758e63',
                           mem_page_size='large',
                           page_sizes=[config.page_1gb])
@pytest.mark.idempotent_id('d2930c9c-2757-4a12-931d-065a3e5a514c',
                           mem_page_size='any',
                           page_sizes=[config.page_2mb, config.page_1gb])
def test_huge_pages_2mb_and_1gb_available(computes_with_hp_mixed,
                                          cirros_image,
                                          keypair,
                                          create_flavor,
                                          flavor_steps,
                                          security_group,
                                          net_subnet_router,
                                          floating_ip,
                                          server_steps,
                                          host_steps,
                                          nfv_steps,
                                          os_faults_steps,
                                          mem_page_size,
                                          page_sizes):
    """**Scenario:** Check server page size when 2Mb and 1Gb are available

    This test checks page size of server created with flavor option
    mem_page_size=large/any on compute with 2Mb and 1Gb pages.

    **Setup:**

    #. Find a compute with HP 2Mb and 1Gb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Create flavor with mem_page_size=large/any
    #. Create server
    #. Attach floating IP to servers
    #. Check HP size of server using dump
    #. Check connectivity from server to 8.8.8.8

    **Teardown:**

    #. Delete server
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    fqdn_mixed = computes_with_hp_mixed[0]
    host_name_mixed = host_steps.get_host(fqdn=fqdn_mixed).host_name

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=2048, vcpus=2, disk=1)
    metadata = {'hw:mem_page_size': mem_page_size}
    flavor_steps.set_metadata(flavor, metadata)

    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD,
        keypair=keypair,
        availability_zone='nova:{}'.format(host_name_mixed))[0]
    server_steps.attach_floating_ip(server, floating_ip)

    server_dump = os_faults_steps.get_server_dump(server)
    nfv_steps.check_server_page_size(server_dump, page_sizes)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.parametrize('computes_with_hp_mixed',
                         [{'host_count': 1, 'hp_count_2mb': 2048,
                           'hp_count_1gb': 4}],
                         indirect=['computes_with_hp_mixed'])
@pytest.mark.parametrize('mem_page_size, page_size',
                         [('large', config.page_2mb),
                          ('any', config.page_2mb),
                          ('large', config.page_1gb),
                          ('any', config.page_1gb)],
                         ids=['large for 2mb', 'any for 2mb',
                              'large for 1gb', 'any for 1gb'])
@pytest.mark.idempotent_id('78ef9e08-3c42-4822-a2d7-2939288be8db',
                           mem_page_size='large', page_size=config.page_2mb)
@pytest.mark.idempotent_id('1f8ba12d-ebdf-4f25-beb8-36660199b4d4',
                           mem_page_size='any', page_size=config.page_2mb)
@pytest.mark.idempotent_id('6fbcb665-6ffb-4a27-8208-204f4e1997ad',
                           mem_page_size='large', page_size=config.page_1gb)
@pytest.mark.idempotent_id('192ce3ea-420a-49e6-8f2a-8d63eeb233c9',
                           mem_page_size='any', page_size=config.page_1gb)
def test_huge_pages_one_type_available(computes_with_hp_mixed,
                                       cirros_image,
                                       keypair,
                                       create_flavor,
                                       flavor_steps,
                                       security_group,
                                       net_subnet_router,
                                       floating_ip,
                                       server_steps,
                                       host_steps,
                                       create_servers_to_allocate_hp,
                                       nfv_steps,
                                       os_faults_steps,
                                       mem_page_size,
                                       page_size):
    """**Scenario:** Check server page size when one of 2Mb/1Gb is available

    This test checks page size of server created with flavor option
    mem_page_size=large/any on compute with 2Mb and 1Gb pages but without free
    pages of one type.

    **Setup:**

    #. Find a compute with HP 2Mb and 1Gb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Create servers to allocate all free 2Mb or 1Gb pages
    #. Create flavor with mem_page_size=large/any
    #. Create server
    #. Attach floating IP to servers
    #. Check HP size of server using dump
    #. Check connectivity from server to 8.8.8.8

    **Teardown:**

    #. Delete server
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    fqdn_mixed = computes_with_hp_mixed[0]
    host_name_mixed = host_steps.get_host(fqdn=fqdn_mixed).host_name

    hp_sizes = [config.page_2mb, config.page_1gb]
    hp_sizes.remove(page_size)
    size_to_allocate = hp_sizes[0]
    create_servers_to_allocate_hp(fqdn_mixed, size_to_allocate)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=2048, vcpus=2, disk=1)
    metadata = {'hw:mem_page_size': mem_page_size}
    flavor_steps.set_metadata(flavor, metadata)

    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD,
        keypair=keypair,
        availability_zone='nova:{}'.format(host_name_mixed))[0]
    server_steps.attach_floating_ip(server, floating_ip)

    server_dump = os_faults_steps.get_server_dump(server)
    nfv_steps.check_server_page_size(server_dump, [page_size])

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.parametrize('computes_with_hp_mixed',
                         [{'host_count': 1, 'hp_count_2mb': 512,
                           'hp_count_1gb': 4}],
                         indirect=['computes_with_hp_mixed'])
@pytest.mark.idempotent_id('4d6d8c3c-24a0-4de2-99be-85c6f33c4eb8')
def test_huge_pages_not_available(computes_with_hp_mixed,
                                  cirros_image,
                                  keypair,
                                  create_flavor,
                                  flavor_steps,
                                  security_group,
                                  net_subnet_router,
                                  floating_ip,
                                  server_steps,
                                  host_steps,
                                  create_servers_to_allocate_hp,
                                  nfv_steps,
                                  os_faults_steps):
    """**Scenario:** Check server page size when HP is not available

    This test checks page size of server created with flavor option
    mem_page_size=any on compute with 2Mb and 1Gb pages but without free pages.

    **Setup:**

    #. Find a compute with HP 2Mb and 1Gb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Create servers to allocate all free 2Mb and 1Gb pages
    #. Create flavor with mem_page_size=any
    #. Create server
    #. Attach floating IP to servers
    #. Check HP size of server using dump
    #. Check connectivity from server to 8.8.8.8

    **Teardown:**

    #. Delete server
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    fqdn_mixed = computes_with_hp_mixed[0]
    host_name_mixed = host_steps.get_host(fqdn=fqdn_mixed).host_name

    create_servers_to_allocate_hp(fqdn_mixed, config.page_2mb)
    create_servers_to_allocate_hp(fqdn_mixed, config.page_1gb)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=2048, vcpus=2, disk=1)
    metadata = {'hw:mem_page_size': 'any'}
    flavor_steps.set_metadata(flavor, metadata)

    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD,
        keypair=keypair,
        availability_zone='nova:{}'.format(host_name_mixed))[0]
    server_steps.attach_floating_ip(server, floating_ip)

    server_dump = os_faults_steps.get_server_dump(server)
    nfv_steps.check_server_page_size(server_dump, None)

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.parametrize('computes_with_hp_mixed',
                         [{'host_count': 1, 'hp_count_2mb': 2048,
                           'hp_count_1gb': 4}],
                         indirect=['computes_with_hp_mixed'])
@pytest.mark.parametrize('page_size',
                         [config.page_2mb, config.page_1gb])
@pytest.mark.idempotent_id('e91adbd7-d334-466f-aebc-8a8b736707c1',
                           page_size=config.page_2mb)
@pytest.mark.idempotent_id('2220d54a-06b2-43a7-ada0-d0c2fa369065',
                           page_size=config.page_1gb)
def test_huge_pages_less_available(computes_with_hp_mixed,
                                   cirros_image,
                                   keypair,
                                   create_flavor,
                                   flavor_steps,
                                   security_group,
                                   net_subnet_router,
                                   floating_ip,
                                   server_steps,
                                   host_steps,
                                   create_servers_to_allocate_hp,
                                   nfv_steps,
                                   os_faults_steps,
                                   page_size):
    """**Scenario:** Check server page size when free 2Mb/1Gb is not enough

    This test checks page size of server created with flavor option
    mem_page_size=large on compute with 2Mb and 1Gb pages but available pages
    of one type is not enough.

    **Setup:**

    #. Find a compute with HP 2Mb and 1Gb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create network, subnet and router
    #. Create floating IP

    **Steps:**

    #. Create servers to allocate free 2Mb or 1Gb pages to keep 1024 Mb
    #. Create flavor with mem_page_size=large and ram=2048
    #. Create server
    #. Attach floating IP to servers
    #. Check HP size of server using dump
    #. Check connectivity from server to 8.8.8.8

    **Teardown:**

    #. Delete server
    #. Delete floating IP
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete keypair
    #. Delete cirros image
    """
    fqdn_mixed = computes_with_hp_mixed[0]
    host_name_mixed = host_steps.get_host(fqdn=fqdn_mixed).host_name

    hp_sizes = [config.page_2mb, config.page_1gb]
    hp_sizes.remove(page_size)
    expected_size = hp_sizes[0]
    create_servers_to_allocate_hp(fqdn_mixed, size=page_size,
                                  ram_left_free=1024)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=2048, vcpus=2, disk=1)
    metadata = {'hw:mem_page_size': 'large'}
    flavor_steps.set_metadata(flavor, metadata)

    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD,
        keypair=keypair,
        availability_zone='nova:{}'.format(host_name_mixed))[0]
    server_steps.attach_floating_ip(server, floating_ip)

    server_dump = os_faults_steps.get_server_dump(server)
    nfv_steps.check_server_page_size(server_dump, [expected_size])

    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP, server_ssh, timeout=config.PING_CALL_TIMEOUT)
