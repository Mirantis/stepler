"""
---------------------
Create VMs tests
---------------------
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

from stepler.third_party.utils import generate_ids


@pytest.mark.testrail_id('1680616')
def test_launch_vm_from_image_using_all_flavors(
        security_group, internal_network, cirros_image, keypair,
        create_server_context, flavor_steps):
    """**Scenario:** Launch VM from image using all standard flavors.

    This test verifies test #1680616

    **Setup:**
        #. Upload cirros image
        #. Create security group with allow ping rule
        #. Create keypair
    **Steps:**
        #. Get list of all flavors
        #. Create and boot server using every flavor
        #. Check that server status is active
    **Teardown:**
        #. Delete servers
        #. Delete security group
        #. Delete keypair
        #. Delete cirros image
    """
    flavors = flavor_steps.get_flavors()

    for flavor in flavors:
        server_name = next(generate_ids(prefix='server', postfix=flavor.name))

        with create_server_context(
                server_name=server_name,
                image=cirros_image,
                flavor=flavor,
                networks=[internal_network],
                keypair=keypair,
                security_groups=[security_group]):
            # check for server state is inside 'create_server_context'
            pass


@pytest.mark.testrail_id('1680618')
def test_launch_vm_from_volume_using_all_flavors(
        security_group, internal_network, cirros_image, keypair, nova_floating_ip,
        create_server_context, create_volume, flavor_steps, server_steps):
    """**Scenario:** Launch VM from volume using all standard flavors.

    This test verifies test #1680618

    **Setup:**
        #. Upload cirros image
        #. Create security group with allow ping rule
        #. Create keypair
        #. Create volume from cirros image
    **Steps:**
        #. Get list of all flavors
        #. Create and boot server from volume using every flavor
        #. Check that server status is active
        #. Assign floating IP to server
        #. Check that server is available via ping
    **Teardown:**
        #. Delete servers
        #. Delete security group
        #. Delete keypair
        #. Delete cirros image
        #. Delete volume
        #. Delete floating IP
    """
    flavors = flavor_steps.get_flavors()

    volume_name = next(generate_ids(prefix='volume'))
    volume = create_volume(
        name=volume_name,
        size=1,  # GB
        image=cirros_image,
        volume_type=None,
        description=None,
        check=True)

    for flavor in flavors:
        server_name = next(generate_ids(prefix='server', postfix=flavor.name))

        with create_server_context(
                server_name=server_name,
                image=None,
                block_device_mapping={'vda': volume.id},
                flavor=flavor,
                networks=[internal_network],
                keypair=keypair,
                security_groups=[security_group]) as vm:

            server_steps.attach_floating_ip(vm, nova_floating_ip)
            server_steps.check_ping_to_server_floating(vm, timeout=5 * 60)
