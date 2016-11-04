"""
----------------------------
Create virtual servers tests
----------------------------
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


@pytest.mark.idempotent_id('e9ab1a51-9204-4760-8c3f-a7fdd8e2f185')
def test_launch_server_from_image_using_all_flavors(
        security_group,
        internal_network,
        cirros_image,
        keypair,
        create_server_context,
        flavor_steps):
    """**Scenario:** Launch server from image using all standard flavors.

    TODO(sandriichenko): launchpad can't find bug 1680616
    This test verifies bug #1680616

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
        server_name = next(utils.generate_ids(
            prefix='server', postfix=flavor.name))

        with create_server_context(
                server_name=server_name,
                image=cirros_image,
                flavor=flavor,
                networks=[internal_network],
                keypair=keypair,
                security_groups=[security_group]):
            # check for server state is inside 'create_server_context'
            pass


@pytest.mark.idempotent_id('904d3614-d98a-4dbf-8fe4-211d025e4de2')
def test_launch_vm_from_volume_using_all_flavors(
        security_group,
        internal_network,
        cirros_image,
        keypair,
        nova_floating_ip,
        create_server_context,
        volume_steps,
        flavor_steps,
        server_steps):
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

    volume = volume_steps.create_volumes(
        names=utils.generate_ids('volume', count=1),
        image=cirros_image)[0]

    for flavor in flavors:
        server_name = next(utils.generate_ids('server', postfix=flavor.name))

        with create_server_context(
                server_name=server_name,
                image=None,
                block_device_mapping={'vda': volume.id},
                flavor=flavor,
                networks=[internal_network],
                keypair=keypair,
                security_groups=[security_group]) as server:

            server_steps.attach_floating_ip(server, nova_floating_ip)
            server_steps.check_ping_to_server_floating(
                server, timeout=config.PING_CALL_TIMEOUT)
