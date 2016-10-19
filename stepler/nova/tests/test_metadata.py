"""
---------------------
Server metadata tests
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

from stepler.third_party import utils


@pytest.mark.idempotent_id('fb831027-2663-4b76-b81f-868a85ca08fe')
def test_metadata_reach_all_booted_vm(
        security_group,
        nova_floating_ip,
        ubuntu_image,
        keypair,
        create_server_context,
        flavor_steps,
        network_steps,
        server_steps):
    """**Scenario:** Verify that image can be connected with SSH.

    **Setup:**

    #. Create security group
    #. Create floating IP
    #. Get or create ubuntu image
    #. Create keypair

    **Steps:**

    #. Get flavor ``m1.small``
    #. Get admin internal network
    #. Create nova server
    #. Attach floating IP to nova server
    #. Check that server is available via SSH
    #. Detach floating IP
    #. Delete nova server

    **Teardown:**

    #. Delete keypair
    #. Release floating IP
    #. Delete security group
    """
    flavor = flavor_steps.get_flavor(name='m1.small')
    network = network_steps.get_network_by_name('admin_internal_net')

    server_name = next(utils.generate_ids('server'))
    with create_server_context(server_name,
                               image=ubuntu_image,
                               flavor=flavor,
                               networks=[network],
                               keypair=keypair,
                               security_groups=[security_group],
                               username='ubuntu') as server:

        server_steps.attach_floating_ip(server, nova_floating_ip)
        server_steps.get_server_ssh(server)
        server_steps.detach_floating_ip(server, nova_floating_ip)
