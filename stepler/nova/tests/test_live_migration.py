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

import time

import pytest

from stepler import config
from stepler.third_party.utils import generate_ids

pytestmark = pytest.mark.usefixtures('disable_nova_config_drive')


def test_network_connectivity_to_vm_during_live_migration(
        live_migration_server, nova_floating_ip, server_steps):
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
        #. Add router interface to created network
        #. Boot server from cirros image
        #. Assign floating ip to server

    **Steps:**

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
    with server_steps.check_ping_loss_context(
            nova_floating_ip.ip, max_loss=20):
        server_steps.live_migrate(live_migration_server, block_migration=True)


@pytest.mark.parametrize(
    'workload', ['CPU', 'memory', 'disk'],
    ids=['CPU workload', 'memory workload', 'disk workload'])
@pytest.mark.parametrize(
    'live_migration_server, block_migration', [
        ({'boot_from_volume': False}, True),
        ({'boot_from_volume': True}, False)],
    ids=['boot_from_image', 'boot_from_volume'],
    indirect=['live_migration_server'])
def test_server_migration_with_workload(live_migration_server,
                                        nova_floating_ip, server_steps,
                                        workload, block_migration):
    """**Scenario:** LM of instance under workload.

    **Setup:**

        #. Upload ubuntu image
        #. Create network
        #. Create subnet
        #. Create router
        #. Set router default gateway to public network
        #. Create security group with allow ping rule
        #. Create flavor
        #. Add router interface to created network
        #. Boot server from image or volume
        #. Assign floating ip to server

    **Steps:**

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
    server = live_migration_server
    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
        if workload == 'CPU':
            server_steps.generate_server_cpu_workload(server_ssh)
        elif workload == 'memory':
            server_steps.generate_server_memory_workload(server_ssh)
        elif workload == 'disk':
            server_steps.generate_server_disk_workload(server_ssh)
    server_steps.live_migrate(server, block_migration=block_migration)
    server_steps.check_ping_to_server_floating(
        server, timeout=config.PING_CALL_TIMEOUT)


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
    timestamp = str(time.time())
    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
        server_steps.create_timestamps_on_root_and_ephemeral_disks(
            server_ssh, timestamp=timestamp)
    with server_steps.check_ping_loss_context(
            nova_floating_ip.ip, max_loss=20):
        server_steps.live_migrate(server, block_migration=True)
    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
        server_steps.check_timestamps_on_root_and_ephemeral_disks(
            server_ssh, timestamp=timestamp)
