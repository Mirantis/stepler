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
def test_allocation_huge_pages_2m(computes_with_hp_2mb,
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
    """**Scenario:** Check allocation 2M HugePages for servers

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
    #. Check HP sizes for all servers using dumps
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
        nfv_steps.check_server_page_size(server_dump, config.page_2mb)

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
@pytest.mark.requires("computes_count >= 3")
@pytest.mark.parametrize('computes_with_hp_2mb',
                         [{'host_count': 2, 'hp_count_per_host': 512}],
                         indirect=['computes_with_hp_2mb'])
@pytest.mark.idempotent_id('35ca47bf-7b41-4ce0-bb74-7ecc01b8586b')
def test_migration_huge_pages_2m(computes_with_hp_2mb,
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
    """**Scenario:** Check cold migration of server with 2M HugePages

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
    #. Check HP sizes for all servers using dumps
    #. Check current HP total and free values on computes
    #. Check connectivity between servers
    #. Migrate server1
    #. Check that server1 is hosted on compute with HP
    #. Check HP sizes for server1 using dumps
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
            keypair=keypair)[0]
        floating_ip = create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)
        servers.append(server)

    for server in servers:
        server_steps.check_server_host_attr(server, host_names=host_names_2mb)

    for server in servers:
        server_dump = os_faults_steps.get_server_dump(server)
        nfv_steps.check_server_page_size(server_dump, config.page_2mb)

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
    nfv_steps.check_server_page_size(server_dump, config.page_2mb)

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
@pytest.mark.requires("computes_count >= 2")
@pytest.mark.parametrize('computes_with_hp_2mb',
                         [{'host_count': 2, 'hp_count_per_host': 1024}],
                         indirect=['computes_with_hp_2mb'])
@pytest.mark.idempotent_id('6ea65424-4ad2-48c6-9dda-0e0da396c97e')
def test_evacuation_huge_pages_2m(computes_with_hp_2mb,
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
    """**Scenario:** Check server evacuation with 2M HugePages

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
    #. Check HP sizes for all servers using dumps
    #. Check current HP total and free values on computes
    #. Check connectivity between servers
    #. Stop nova-compute on host1 and force service to down
    #. Evacuate server1
    #. Unset force service to down and start nova-compute on host1
    #. Check HP sizes for servers using dumps
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
        nfv_steps.check_server_page_size(server_dump, config.page_2mb)

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
        nfv_steps.check_server_page_size(server_dump, config.page_2mb)

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
