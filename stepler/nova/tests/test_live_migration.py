"""
-------------------------
Nova live migration tests
-------------------------
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

from stepler.third_party.utils import generate_ids


def test_network_connectivity_to_vm_during_live_migration(
        keypair, flavor, security_group, nova_floating_ip, cirros_image,
        network, subnet, router, add_router_interfaces, create_volume,
        create_server, server_steps):
    """**Scenario:** Verify network connectivity to the VM during live
    migration.

    **Setup:**

        #. Upload cirros image
        #. Create network
        #. Create subnet
        #. Create router
        #. Set router default gateway to public network
        #. Create security group with allow ping rule
        #. Create flavor

    **Steps:**

        #. Add router interface to created network
        #. Boot server from cirros image
        #. Assign floating ip to server
        #. Start ping to server floating ip
        #. Migrate server to another hypervisor
        #. Stop ping
        #. Check that ping loss is not more than 20

    **Teardown:**

        #. Delete server
        #. Delete flavor
        #. Delete security group
        #. Delete router
        #. Delete subnet
        #. Delete network
        #. Delete cirros image
    """
    add_router_interfaces(router, [subnet])
    server_name = next(generate_ids('server'))
    server = create_server(server_name,
                           image=cirros_image,
                           keypair=keypair,
                           flavor=flavor,
                           networks=[network],
                           security_groups=[security_group])
    server_steps.attach_floating_ip(server, nova_floating_ip)
    with server_steps.check_ping_loss_context(nova_floating_ip.ip,
                                              max_loss=20):
        server_steps.live_migrate(server, block_migration=True)
