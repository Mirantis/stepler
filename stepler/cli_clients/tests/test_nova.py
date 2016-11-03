"""
-------------------------
Tests for nova CLI client
-------------------------
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


@pytest.mark.idempotent_id('c6c11d30-f0b0-4574-b501-e111c3c631f1')
def test_nova_list(server, cli_nova_steps):
    """**Scenario:** nova list works via shell.

    **Setup:**:

    #. Create nova server and wait it active

    **Steps:**:

    #. Execute in shell ``nova list``

    **Teardown:**

    #. Remove nova server
    """
    cli_nova_steps.nova_list()


# TODO(ssokolov) add check of condition 'two or more nodes'
@pytest.mark.idempotent_id('b7ca17e5-aff3-4799-9e3f-c4f0595c20b5')
def test_live_evacuation(cirros_image,
                         flavor,
                         network,
                         subnet,
                         router,
                         keypair,
                         security_group,
                         add_router_interfaces,
                         nova_create_floating_ip,
                         hypervisor_steps,
                         cli_nova_steps,
                         server_steps):
    """**Scenario:** Live evacuate all instances of the specified host to
    other available hosts without shared storage.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create net and subnet
    #. Create router
    #. Create keypair
    #. Create security group

    **Steps:**

    #. Set router default gateway to public network
    #. Create two instances on node-1
    #. Assign floating ip for instances
    #. Execute 'nova host-evacuate-live' to node-2
    #. Check that instances are hosted on node-2
    #. Check ping between instances

    **Teardown:**

    #. Delete instances
    #. Delete security group
    #. Delete keypair
    #. Delete net and subnet
    #. Delete flavor
    #. Delete cirros image
    """
    add_router_interfaces(router, [subnet])

    hypervisors = hypervisor_steps.get_hypervisors()
    host_name_1 = hypervisors[0].hypervisor_hostname
    host_name_2 = hypervisors[1].hypervisor_hostname

    servers = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        keypair=keypair,
        security_groups=[security_group],
        availability_zone='nova:' + host_name_1,
        username=config.CIRROS_USERNAME)

    for server in servers:
        floating_ip = nova_create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)

    cli_nova_steps.live_evacuate(host_name_1, host_name_2, servers)

    # after evacuate, server status is changed: Active -> Migrating -> Active
    for server in servers:
        server_steps.check_server_status(
            server,
            config.STATUS_MIGRATING,
            timeout=config.MIGRATION_START_TIMEOUT)
    for server in servers:
        server_steps.check_server_status(
            server,
            config.STATUS_ACTIVE,
            transit_statuses=[config.STATUS_MIGRATING],
            timeout=config.LIVE_EVACUATE_TIMEOUT)

    for server in servers:
        server_steps.check_instance_hypervisor_hostname(server, host_name_2)

    server_steps.check_ping_between_servers(
        servers, ip_type='floating',
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
