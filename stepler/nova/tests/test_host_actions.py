"""
-----------------------------
Nova host actions tests
-----------------------------
"""
#    Copyright 2016 Mirantis, Inc.
#
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


@pytest.mark.idempotent_id('00f1721e-7aa7-45eb-851a-2b5d086caead')
def test_migrate_instances(
        cirros_image,
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

    server_names = utils.generate_ids(prefix='server', count=3)
    servers = create_servers(server_names, cirros_image, flavor,
                             networks=[network],
                             keypair=keypair,
                             security_groups=[security_group],
                             availability_zone=availability_zone,
                             username='cirros')
    server_steps.migrate_servers(servers)
    server_steps.confirm_resize_servers(servers)

    for server in servers:
        floating_ip = nova_create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
