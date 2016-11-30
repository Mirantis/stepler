"""
---------------------------
Ironic baremetal node tests
---------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from stepler import config


@pytest.mark.idempotent_id('0a9792ce-9933-479d-8ed2-b1adfafcae62')
def test_boot_servers_concurrently_on_ironic_node(keypair,
                                                  baremetal_flavor,
                                                  baremetal_ubuntu_image,
                                                  baremetal_network,
                                                  nova_create_floating_ip,
                                                  server_steps,
                                                  ironic_node_steps):
    """**Scenario:** Hard reboot server on ironic node.

    **Setup:**

    #. Create keypair
    #. Create baremetal flavor
    #. Upload baremetal ubuntu image

    **Steps:**

    #. Create and boot server_1 and server_2
    #. Check that servers status is active
    #. Get ironic_node_1
    #. Get ironic_node_2
    #. Check that ironic nodes provision state is active
    #. Create floating ip  for server_1
    #. Attach floating ip to server_2
    #. Create floating ip  for server_2
    #. Attach floating ip to server_2
    #. Check ssh access to server_1
    #. Check ssh access to server_2

    **Teardown:**

    #. Delete servers
    #. Delete floating ips
    #. Delete image
    #. Delete flavor
    #. Delete keypair
    """
    server_1, server_2 = server_steps.create_servers(
        image=baremetal_ubuntu_image,
        flavor=baremetal_flavor,
        count=2,
        networks=[baremetal_network],
        keypair=keypair,
        username=config.UBUNTU_USERNAME)

    ironic_node_1 = ironic_node_steps.get_ironic_node(
        instance_uuid=server_1.id)
    ironic_node_2 = ironic_node_steps.get_ironic_node(
        instance_uuid=server_2.id)

    ironic_node_steps.check_ironic_nodes_provision_state(
        [ironic_node_1, ironic_node_2], config.STATUS_ACTIVE)

    server_steps.attach_floating_ip(server_1, nova_create_floating_ip())
    server_steps.attach_floating_ip(server_2, nova_create_floating_ip())

    server_steps.get_server_ssh(server_1)
    server_steps.get_server_ssh(server_2)


@pytest.mark.idempotent_id('6f241b44-a3b2-48e8-8cf2-422137b6851b')
def test_boot_servers_consequently_on_ironic_node(keypair,
                                                  baremetal_flavor,
                                                  baremetal_ubuntu_image,
                                                  baremetal_network,
                                                  nova_create_floating_ip,
                                                  server_steps,
                                                  ironic_node_steps):
    """**Scenario:** Hard reboot server on ironic node.

    **Setup:**

    #. Create keypair
    #. Create baremetal flavor
    #. Upload baremetal ubuntu image

    **Steps:**

    #. Create and boot server_1
    #. Check that server_1 status is active
    #. Create and boot server_2
    #. Check that server_2 status is active
    #. Get ironic_node_1
    #. Get ironic_node_1
    #. Check that ironic nodes provision state is active
    #. Create floating ip  for server_1
    #. Attach floating ip to server_2
    #. Create floating ip  for server_2
    #. Attach floating ip to server_2
    #. Check ssh access to server_1
    #. Check ssh access to server_2

    **Teardown:**

    #. Delete servers
    #. Delete floating ips
    #. Delete image
    #. Delete flavor
    #. Delete keypair
    """
    server_1 = server_steps.create_servers(image=baremetal_ubuntu_image,
                                           flavor=baremetal_flavor,
                                           networks=[baremetal_network],
                                           keypair=keypair,
                                           username=config.UBUNTU_USERNAME)[0]

    server_2 = server_steps.create_servers(image=baremetal_ubuntu_image,
                                           flavor=baremetal_flavor,
                                           networks=[baremetal_network],
                                           keypair=keypair,
                                           username=config.UBUNTU_USERNAME)[0]

    ironic_node_1 = ironic_node_steps.get_ironic_node(
        instance_uuid=server_1.id)
    ironic_node_2 = ironic_node_steps.get_ironic_node(
        instance_uuid=server_2.id)

    ironic_node_steps.check_ironic_nodes_provision_state(
        [ironic_node_1, ironic_node_2], config.STATUS_ACTIVE)

    server_steps.attach_floating_ip(server_1, nova_create_floating_ip())
    server_steps.attach_floating_ip(server_2, nova_create_floating_ip())

    server_steps.get_server_ssh(server_1)
    server_steps.get_server_ssh(server_2)


@pytest.mark.idempotent_id('db942db2-59c8-4736-9b00-58635a157c77')
def test_hard_reboot_server_on_ironic_node(keypair,
                                           baremetal_flavor,
                                           baremetal_ubuntu_image,
                                           baremetal_network,
                                           nova_floating_ip,
                                           server_steps):
    """**Scenario:** Hard reboot server on ironic node.

    **Setup:**

    #. Create keypair
    #. Create baremetal flavor
    #. Upload baremetal ubuntu image
    #. Create floating ip

    **Steps:**

    #. Create and boot server
    #. Check that server status is active
    #. Attach floating ip to server
    #. Check ssh access to server
    #. Reboot server
    #. Check that server status is hard reboot
    #. Check that server status is active
    #. Check ssh access to server

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete image
    #. Delete flavor
    #. Delete keypair
    """
    server = server_steps.create_servers(image=baremetal_ubuntu_image,
                                         flavor=baremetal_flavor,
                                         networks=[baremetal_network],
                                         keypair=keypair,
                                         username=config.UBUNTU_USERNAME)[0]
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.get_server_ssh(server)
    server_steps.reboot_server(server, reboot_type=config.REBOOT_HARD)
    server_steps.get_server_ssh(server)


@pytest.mark.idempotent_id('9e1ce800-1873-4471-9903-5f2433a412f6')
def test_stop_start_server_on_baremetal_node(keypair,
                                             baremetal_flavor,
                                             baremetal_ubuntu_image,
                                             baremetal_network,
                                             nova_floating_ip,
                                             server_steps):
    """**Scenario:** Shut off and restart server on baremetal node.

    **Setup:**

    #. Create keypair
    #. Create baremetal flavor
    #. Upload baremetal ubuntu image
    #. Create floating ip

    **Steps:**

    #. Create and boot server
    #. Check that server status is active
    #. Attach floating ip to server
    #. Check ssh access to server
    #. Stop server
    #. Check that server status is shutoff
    #. Start server
    #. Check that server status is active
    #. Check ssh access to server

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete image
    #. Delete flavor
    #. Delete keypair
    """
    server = server_steps.create_servers(image=baremetal_ubuntu_image,
                                         flavor=baremetal_flavor,
                                         networks=[baremetal_network],
                                         keypair=keypair,
                                         username=config.UBUNTU_USERNAME)[0]
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.get_server_ssh(server)
    server_steps.stop_server(server)
    server_steps.start_server(server)
    server_steps.get_server_ssh(server)


@pytest.mark.idempotent_id('fce98286-30c1-420d-8d35-7660907ec1ff')
def test_create_server_on_baremetal_node(keypair,
                                         baremetal_ubuntu_image,
                                         baremetal_flavor,
                                         baremetal_network,
                                         nova_floating_ip,
                                         server_steps):
    """**Scenario:** Launch server on baremetal node.

    **Setup:**

    #. Create keypair
    #. Create baremetal flavor
    #. Upload baremetal ubuntu image
    #. Create floating ip

    **Steps:**

    #. Create and boot server
    #. Check that server status is active
    #. Attach floating ip to server
    #. Check ssh access to server

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete image
    #. Delete flavor
    #. Delete keypair
    """
    server = server_steps.create_servers(image=baremetal_ubuntu_image,
                                         flavor=baremetal_flavor,
                                         networks=[baremetal_network],
                                         keypair=keypair,
                                         username=config.UBUNTU_USERNAME)[0]
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.get_server_ssh(server)


@pytest.mark.idempotent_id('3c48b915-1e2e-4800-af8b-3d249610dd50')
def test_create_server_on_baremetal_node_in_maintenance_state(
        ironic_node_steps,
        baremetal_network,
        baremetal_ubuntu_image,
        baremetal_flavor,
        server_steps):
    """**Scenario:** Launch server on baremetal node in maintenance state.

    **Setup:**

    #. Create baremetal flavor
    #. Upload baremetal ubuntu image

    **Steps:**

    #. Get Ironic nodes
    #. Set all Ironic nodes into maintenance mode
    #. Create and boot server
    #. Check that server status is error

    **Teardown:**

    #. Delete server
    #. Delete image
    #. Delete flavor
    """
    ironic_nodes = ironic_node_steps.get_ironic_nodes()
    ironic_node_steps.set_ironic_nodes_maintenance(nodes=ironic_nodes,
                                                   state='on')

    server = server_steps.create_servers(image=baremetal_ubuntu_image,
                                         networks=[baremetal_network],
                                         flavor=baremetal_flavor,
                                         username=config.UBUNTU_USERNAME,
                                         check=False)[0]
    server_steps.check_server_status(server=server,
                                     expected_statuses=config.STATUS_ERROR)
