"""
-----------------------
Nova host actions tests
-----------------------
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


@pytest.mark.idempotent_id('2eb54a35-7218-4220-b376-8aa5f1b6f74f')
@pytest.mark.requires("computes_count >= 2")
def test_host_resources_info(cirros_image,
                             flavor,
                             network,
                             subnet,
                             server_steps,
                             host_steps):
    """**Scenario:** Get info about resources' usage on nodes.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create net and subnet

    **Steps:**

    #. Get resource info for node-1 and node-2
    #. Create two servers on node-1
    #. Get resource info for node-1 and check that resource usage is
       changed and project_id is present in results
    #. Get resource info for node-2 and check that resource usage is
       not changed
    #. Create two servers on node-2
    #. Get resource info for node-1 and check that resource usage is
       not changed
    #. Get resource info for node-2 and check that resource usage is
       changed and project_id is present in results

    **Teardown:**

    #. Delete servers
    #. Delete net and subnet
    #. Delete flavor
    #. Delete cirros image
    """
    hosts = [host for host in host_steps.get_hosts() if host.zone == 'nova']
    host_1 = hosts[0]
    host_2 = hosts[1]
    usage_data_1 = host_steps.get_usage_data(host_1)
    usage_data_2 = host_steps.get_usage_data(host_2)

    servers_host_1 = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        availability_zone='nova:' + host_1.host_name,
        username=config.CIRROS_USERNAME)

    project_id = servers_host_1[0].tenant_id
    host_steps.check_host_usage_changing(host_1,
                                         usage_data_1,
                                         changed=True,
                                         project_id=project_id)
    host_steps.check_host_usage_changing(host_2,
                                         usage_data_2,
                                         changed=False)

    usage_data_1 = host_steps.get_usage_data(host_1)
    usage_data_2 = host_steps.get_usage_data(host_2)

    servers_host_2 = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        availability_zone='nova:' + host_2.host_name,
        username=config.CIRROS_USERNAME)

    project_id = servers_host_2[0].tenant_id
    host_steps.check_host_usage_changing(host_1,
                                         usage_data_1,
                                         changed=False)
    host_steps.check_host_usage_changing(host_2,
                                         usage_data_2,
                                         changed=True,
                                         project_id=project_id)


@pytest.mark.idempotent_id('ffc320c3-5688-4442-bcc5-05ae51788d2e')
@pytest.mark.requires("computes_count >= 2")
def test_migrate_servers(cirros_image,
                         net_subnet_router,
                         security_group,
                         flavor,
                         keypair,
                         nova_availability_zone_hosts,
                         server_steps,
                         nova_create_floating_ip):
    """**Scenario:** Migrate servers from the specified host to other hosts.

    **Setup:**

    #. Upload cirros image
    #. Create network, subnet, router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor

    **Steps:**

    #. Boot 3 servers on the same hypervisor
    #. Start migration for all servers
    #. Check that every server is rescheduled to other hypervisor
    #. Confirm resize for every server
    #. Check that every migrated server has an ACTIVE status
    #. Assign floating ip for all servers
    #. Send pings between all servers to check network connectivity

    **Teardown:**

    #. Delete servers
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete cirros image
    """
    servers = server_steps.create_servers(
        count=3,
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        keypair=keypair,
        security_groups=[security_group],
        availability_zone='nova:' + nova_availability_zone_hosts[0],
        username=config.CIRROS_USERNAME)

    server_steps.migrate_servers(servers)
    server_steps.confirm_resize_servers(servers)

    for server in servers:
        floating_ip = nova_create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
