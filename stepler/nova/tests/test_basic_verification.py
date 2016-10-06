"""
-----------------------------
Nova basic verification tests
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

from stepler.third_party.utils import generate_ids


def test_boot_instance_from_volume_bigger_than_flavor(
        flavor, security_group, nova_floating_ip, cirros_image, network,
        subnet, router, add_router_interfaces, create_volume, create_server,
        server_steps):
    """**Scenario:** Boot instance from volume bigger than flavor size.

    This test verify bug #1517671

    **Setup:**
        #. Upload cirros image
        #. Create network
        #. Create subnet
        #. Create router
        #. Create security group with allow ping rule
        #. Create flavor
    **Steps:**
        #. Set router default gateway to public network
        #. Add router interface to created network
        #. Create volume from cirros image with disk size bigger than flavor
        #. Boot server from volume
        #. Assign floating ip to server
        #. Check that ping to server's floating ip is successful
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
    volume_size = flavor.disk + 1
    volume = create_volume(
        next(generate_ids('volume')),
        size=volume_size,
        image=cirros_image)
    block_device_mapping = {'vda': volume.id}

    server_name = next(generate_ids('server'))
    server = create_server(server_name,
                           image=None,
                           flavor=flavor,
                           network=network,
                           security_groups=[security_group],
                           block_device_mapping=block_device_mapping)

    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.check_ping_to_server_floating(server, timeout=5 * 60)
