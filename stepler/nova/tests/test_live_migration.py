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

import pytest

from stepler import config
from stepler.third_party.utils import generate_ids

USERDATA_DONE_MARKER = next(generate_ids('userdata-done'))

INSTALL_WORKLOAD_USERDATA = """#!/bin/bash -v
apt-get install -yq stress cpulimit sysstat iperf
echo {}""".format(USERDATA_DONE_MARKER)


def test_network_connectivity_to_vm_during_live_migration(
        keypair,
        flavor,
        security_group,
        nova_floating_ip,
        cirros_image,
        network,
        subnet,
        router,
        add_router_interfaces,
        create_volume,
        create_server,
        server_steps):
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
    server = create_server(
        server_name,
        image=cirros_image,
        keypair=keypair,
        flavor=flavor,
        networks=[network],
        security_groups=[security_group])
    server_steps.attach_floating_ip(server, nova_floating_ip)
    with server_steps.check_ping_loss_context(
            nova_floating_ip.ip, max_loss=20):
        server_steps.live_migrate(server, block_migration=True)


@pytest.mark.parametrize(
    'workload', ['CPU', 'memory', 'disk'],
    ids=['CPU workload', 'memory workload', 'disk workload'])
def test_instance_booted_from_image_migration_with_workload(
        keypair,
        flavor,
        security_group,
        nova_floating_ip,
        ubuntu_image,
        network,
        subnet,
        router,
        add_router_interfaces,
        create_volume,
        create_server,
        ssh_to_instance,
        server_steps,
        workload):
    """**Scenario:** LM of instance booted from image under workload.

    **Setup:**

        #. Upload ubuntu image
        #. Create network
        #. Create subnet
        #. Create router
        #. Set router default gateway to public network
        #. Create security group with allow ping rule
        #. Create flavor

    **Steps:**

        #. Add router interface to created network
        #. Boot server from image
        #. Assign floating ip to server
        #. Start workload on server
        #. Migrate server to another hypervisor
        #. Check that ping to server's floating ip is successful

    **Teardown:**

        #. Delete server
        #. Delete flavor
        #. Delete security group
        #. Delete router
        #. Delete subnet
        #. Delete network
        #. Delete ubuntu image
    """
    add_router_interfaces(router, [subnet])
    server_name = next(generate_ids('server'))
    block_migration = True
    server = create_server(
        server_name,
        image=ubuntu_image,
        flavor=flavor,
        keypair=keypair,
        networks=[network],
        security_groups=[security_group],
        userdata=INSTALL_WORKLOAD_USERDATA,
        username='ubuntu')
    server_steps.check_server_log(
        server,
        USERDATA_DONE_MARKER,
        timeout=config.USERDATA_EXECUTING_TIMEOUT)
    server_steps.attach_floating_ip(server, nova_floating_ip)
    with ssh_to_instance(server, nova_floating_ip.ip) as remote:
        if workload == 'CPU':
            server_steps.server_cpu_workload(remote)
        elif workload == 'memory':
            server_steps.server_mem_workload(remote)
        elif workload == 'disk':
            server_steps.server_disk_workload(remote)
    server_steps.live_migrate(server, block_migration=block_migration)
    server_steps.check_ping_to_server_floating(server, timeout=5 * 60)


@pytest.mark.parametrize(
    'workload', ['CPU', 'memory', 'disk'],
    ids=['CPU workload', 'memory workload', 'disk workload'])
def test_instance_booted_from_volume_migration_with_workload(
        keypair,
        flavor,
        security_group,
        nova_floating_ip,
        ubuntu_image,
        network,
        subnet,
        router,
        add_router_interfaces,
        create_volume,
        create_server,
        ssh_to_instance,
        server_steps,
        workload):
    """**Scenario:** LM of instance booted from volume under workload.

    **Setup:**

        #. Upload ubuntu image
        #. Create network
        #. Create subnet
        #. Create router
        #. Set router default gateway to public network
        #. Create security group with allow ping rule
        #. Create flavor

    **Steps:**

        #. Add router interface to created network
        #. Create volume from image
        #. Boot server from it
        #. Assign floating ip to server
        #. Start workload on server
        #. Migrate server to another hypervisor
        #. Check that ping to server's floating ip is successful

    **Teardown:**

        #. Delete server
        #. Delete flavor
        #. Delete volume
        #. Delete security group
        #. Delete router
        #. Delete subnet
        #. Delete network
        #. Delete ubuntu image
    """
    add_router_interfaces(router, [subnet])
    server_name = next(generate_ids('server'))
    block_migration = False
    volume = create_volume(
        next(generate_ids('volume')), size=20, image=ubuntu_image)
    block_device_mapping = {'vda': volume.id}

    server = create_server(
        server_name,
        image=None,
        flavor=flavor,
        keypair=keypair,
        networks=[network],
        security_groups=[security_group],
        block_device_mapping=block_device_mapping,
        userdata=INSTALL_WORKLOAD_USERDATA,
        username='ubuntu')

    server_steps.check_server_log(
        server,
        USERDATA_DONE_MARKER,
        timeout=config.USERDATA_EXECUTING_TIMEOUT)
    server_steps.attach_floating_ip(server, nova_floating_ip)
    with ssh_to_instance(server, nova_floating_ip.ip) as remote:
        if workload == 'CPU':
            server_steps.server_cpu_workload(remote)
        elif workload == 'memory':
            server_steps.server_mem_workload(remote)
        elif workload == 'disk':
            server_steps.server_disk_workload(remote)
    server_steps.live_migrate(server, block_migration=block_migration)
    server_steps.check_ping_to_server_floating(server, timeout=5 * 60)


def test_migration_with_ephemeral_disk(
        keypair,
        security_group,
        nova_floating_ip,
        cirros_image,
        network,
        subnet,
        router,
        add_router_interfaces,
        create_flavor,
        create_server,
        ssh_to_instance,
        server_steps):
    """**Scenario:** LM of VM with data on root and ephemeral disk.

    **Setup:**

        #. Upload cirros image
        #. Create network
        #. Create subnet
        #. Create router
        #. Set router default gateway to public network
        #. Create security group with allow ping rule

    **Steps:**

        #. Add router interface to created network
        #. Create flavor woth ephemeral disk
        #. Boot server from cirros image with created flavor
        #. Assign floating ip to server
        #. Create timestamp on on root and ephemeral disks
        #. Start ping instance
        #. Migrate server to another hypervisor
        #. Stop ping
        #. Check that ping loss is not more than 20
        #. Verify timestamp on root and ephemeral disks

    **Teardown:**

        #. Delete server
        #. Delete flavor
        #. Delete volume
        #. Delete security group
        #. Delete router
        #. Delete subnet
        #. Delete network
        #. Delete cirros image
    """
    add_router_interfaces(router, [subnet])
    flavor = create_flavor(
        next(generate_ids('flavor')), ram=64, disk=1, vcpus=1, ephemeral=1)

    server_name = next(generate_ids('server'))
    server = create_server(
        server_name,
        image=cirros_image,
        flavor=flavor,
        keypair=keypair,
        networks=[network],
        security_groups=[security_group],
        username='cirros')
    server_steps.attach_floating_ip(server, nova_floating_ip)
    with ssh_to_instance(server, nova_floating_ip.ip) as remote:
        server_steps.create_timestamps_on_root_and_ephemeral(
            remote, check=False)
    with server_steps.check_ping_loss_context(
            nova_floating_ip.ip, max_loss=20):
        server_steps.live_migrate(server, block_migration=True)
    with ssh_to_instance(server, nova_floating_ip.ip) as remote:
        server_steps.check_timestamps_on_root_and_ephemeral(remote)
