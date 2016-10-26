"""
-----------------------
Nova host actions tests
-----------------------
"""

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('2eb54a35-7218-4220-b376-8aa5f1b6f74f')
def test_host_resources_info(cirros_image,
                             flavor,
                             network,
                             subnet,
                             keypair,
                             security_group,
                             create_servers,
                             hypervisor_steps,
                             host_steps):
    """**Scenario:** Get info about resources' usage on nodes

    **Setup:**

        #. Create cirros image
        #. Create flavor
        #. Create net and subnet
        #. Create keypair
        #. Create security group

    **Steps:**

        #. Get resource info for node-1 and node-2
        #. Create two instances on node-1
        #. Get resource info for node-1 and check that resource usage is
           changed and project_id appears in results
        #. Get resource info for node-2 and check that resource usage is
           not changed
        #. Create two instances on node-2
        #. Get resource info for node-1 and check that resource usage is
           not changed
        #. Get resource info for node-2 and check that resource usage is
           changed and project_id appears in results

    **Teardown:**

        #. Delete instances
        #. Delete security group
        #. Delete keypair
        #. Delete net and subnet
        #. Delete flavor
        #. Delete cirros image
    """
    hypervisors = hypervisor_steps.get_hypervisors()
    host_name_1 = hypervisors[0].hypervisor_hostname
    host_name_2 = hypervisors[1].hypervisor_hostname
    host_1 = host_steps.get_host(host_name_1)
    host_2 = host_steps.get_host(host_name_2)

    usage_data_1 = host_steps.get_usage_data(host_1)
    usage_data_2 = host_steps.get_usage_data(host_2)

    server_names = utils.generate_ids('server', count=2)
    availability_zone = 'nova:' + host_name_1
    servers_host_1 = create_servers(server_names, cirros_image, flavor,
                                    networks=[network],
                                    keypair=keypair,
                                    security_groups=[security_group],
                                    availability_zone=availability_zone,
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

    server_names = utils.generate_ids('server', count=2)
    availability_zone = 'nova:' + host_name_2
    servers_host_2 = create_servers(server_names, cirros_image, flavor,
                                    networks=[network],
                                    keypair=keypair,
                                    security_groups=[security_group],
                                    availability_zone=availability_zone,
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
def test_migrate_instances(cirros_image,
                           network,
                           subnet,
                           router,
                           security_group,
                           flavor,
                           add_router_interfaces,
                           keypair,
                           hypervisor_steps,
                           create_servers,
                           server_steps,
                           nova_create_floating_ip):
    """**Scenario:** Migrate instances from the specified host to other hosts

    **Setup:**

        #. Upload cirros image
        #. Create network
        #. Create subnet
        #. Create router
        #. Create security group with allowed ping and ssh rules
        #. Create flavor

    **Steps:**

        #. Set router default gateway to public network
        #. Add router interface to created network
        #. Boot 3 servers on the same hypervisor
        #. Start migration for all servers
        #. Check that every instance is rescheduled to other hypervisor
        #. Confirm resize for every instance
        #. Check that every migrated instance has an ACTIVE status
        #. Assign floating ip for all servers.
        #. Send pings between all servers to check network connectivity

    **Teardown:**
        #. Delete all servers
        #. Delete flavor
        #. Delete security group
        #. Delete router
        #. Delete subnet
        #. Delete network
        #. Delete cirros image
    """
    add_router_interfaces(router, [subnet])

    hypervisor = hypervisor_steps.get_hypervisors()[0]
    availability_zone = 'nova:' + hypervisor.hypervisor_hostname

    server_names = utils.generate_ids('server', count=3)
    servers = create_servers(server_names, cirros_image, flavor,
                             networks=[network],
                             keypair=keypair,
                             security_groups=[security_group],
                             availability_zone=availability_zone,
                             username=config.CIRROS_USERNAME)
    server_steps.migrate_servers(servers)
    server_steps.confirm_resize_servers(servers)

    for server in servers:
        floating_ip = nova_create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
