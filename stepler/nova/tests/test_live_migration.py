"""
-------------------------
Nova live migration tests
-------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import time

import pytest

from stepler import config
from stepler.third_party.utils import generate_ids

pytestmark = [
    pytest.mark.usefixtures('skip_live_migration_tests',
                            'disable_nova_config_drive'),
    pytest.mark.requires("computes_count >= 2")
]


@pytest.mark.idempotent_id('12c72e88-ca87-400b-9fbb-a35c1d07cbda')
@pytest.mark.parametrize('block_migration', [True])
def test_network_connectivity_to_vm_after_live_migration(
        floating_ip,
        server,
        server_steps,
        block_migration):
    """**Scenario:** Verify connectivity to the VM after live migration.

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

    #. Migrate server to another hypervisor
    #. Start ping
    #. Check that pings reach the server succesfully

    **Teardown:**

    #. Delete server
    #. Delete flavor
    #. Delete security group
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(server, floating_ip)
    server_steps.live_migrate([server], block_migration=block_migration)
    server_steps.check_ping_to_server_floating(
        server, timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.idempotent_id('f472898f-7b50-4388-94a4-294b4db5ad7a',
                           block_migration=True)
@pytest.mark.idempotent_id('af78187b-85ee-48fa-8795-274a21b98fa7',
                           block_migration=False)
@pytest.mark.parametrize(
    'live_migration_server, block_migration', [
        ({'boot_from_volume': False}, True),
        ({'boot_from_volume': True}, False)],
    ids=['boot_from_image', 'boot_from_volume'],
    indirect=['live_migration_server'])
@pytest.mark.destructive
def test_server_migration_with_cpu_workload(live_migration_server,
                                            floating_ip, server_steps,
                                            block_migration):
    """**Scenario:** LM of instance under CPU workload.

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

    #. Start CPU workload on server
    #. Migrate server to another hypervisor
    #. Check that ping to server's floating ip is successful
    #. Delete server

    **Teardown:**

    #. Delete flavor
    #. Delete security group
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete ubuntu image
    """
    server = live_migration_server
    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.generate_server_cpu_workload(server_ssh)
    server_steps.live_migrate([server], block_migration=block_migration)
    server_steps.check_ping_to_server_floating(
        server, timeout=config.PING_CALL_TIMEOUT)

    server_steps.delete_servers([server])


@pytest.mark.idempotent_id('27d2c48a-018b-4561-b9a7-c512f9f88e8b',
                           block_migration=True)
@pytest.mark.idempotent_id('f1ad5064-8376-49ef-a0e6-0ee13225d8e6',
                           block_migration=False)
@pytest.mark.parametrize(
    'live_migration_server, block_migration', [
        ({'boot_from_volume': False}, True),
        ({'boot_from_volume': True}, False)
    ],
    ids=['boot_from_image', 'boot_from_volume'],
    indirect=['live_migration_server'])
@pytest.mark.destructive
def test_server_migration_with_memory_workload(live_migration_server,
                                               floating_ip, server_steps,
                                               block_migration):
    """**Scenario:** LM of instance under memory workload.

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

    #. Start memory workload on server
    #. Migrate server to another hypervisor
    #. Check that ping to server's floating ip is successful
    #. Delete server

    **Teardown:**

    #. Delete flavor
    #. Delete security group
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete ubuntu image
    """
    server = live_migration_server
    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.generate_server_memory_workload(server_ssh)
    server_steps.live_migrate([server], block_migration=block_migration)
    server_steps.check_ping_to_server_floating(
        server, timeout=config.PING_CALL_TIMEOUT)

    server_steps.delete_servers([server])


@pytest.mark.idempotent_id('7ba9014f-d615-400e-924c-723f45713748',
                           block_migration=True)
@pytest.mark.idempotent_id('3d884a0e-4b9b-4e97-9099-306de74777fa',
                           block_migration=False)
@pytest.mark.parametrize(
    'live_migration_server, block_migration', [
        ({'boot_from_volume': False}, True),
        ({'boot_from_volume': True}, False)],
    ids=['boot_from_image', 'boot_from_volume'],
    indirect=['live_migration_server'])
@pytest.mark.destructive
def test_server_migration_with_disk_workload(live_migration_server,
                                             floating_ip, server_steps,
                                             block_migration):
    """**Scenario:** LM of instance under disk workload.

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

    #. Start disk workload on server
    #. Migrate server to another hypervisor
    #. Check that ping to server's floating ip is successful
    #. Delete server

    **Teardown:**

    #. Delete flavor
    #. Delete security group
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete ubuntu image
    """
    server = live_migration_server
    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.generate_server_disk_workload(server_ssh)
    server_steps.live_migrate([server], block_migration=block_migration)
    server_steps.check_ping_to_server_floating(
        server, timeout=config.PING_CALL_TIMEOUT)

    server_steps.delete_servers([server])


@pytest.mark.idempotent_id('f5bccac0-c45f-4dcc-b955-55af429de7b3',
                           block_migration=True)
@pytest.mark.idempotent_id('26d1cbf4-1c42-415a-9ce0-07293d504584',
                           block_migration=False)
@pytest.mark.parametrize(
    'live_migration_server, block_migration', [
        ({'boot_from_volume': False}, True),
        ({'boot_from_volume': True}, False)],
    ids=['boot_from_image', 'boot_from_volume'],
    indirect=['live_migration_server'])
@pytest.mark.destructive
def test_server_migration_with_network_workload(
        live_migration_server, security_group, floating_ip,
        neutron_security_group_rule_steps, server_steps, generate_traffic,
        block_migration):
    """**Scenario:** LM of instance under network workload.

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

    #. Start network workload on server
    #. Migrate server to another hypervisor
    #. Check that ping to server's floating ip is successful
    #. Delete server

    **Teardown:**

    #. Delete flavor
    #. Delete security group
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete ubuntu image
    """
    server = live_migration_server
    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        port = 5010
        neutron_security_group_rule_steps.add_rule_to_group(
            security_group['id'],
            direction=config.INGRESS,
            protocol='tcp',
            port_range_min=port,
            port_range_max=port,
            remote_ip_prefix='0.0.0.0/0')
        server_steps.server_network_listen(server_ssh, port=port)
        stop_traffic = generate_traffic(floating_ip['floating_ip_address'],
                                        port)
    server_steps.live_migrate([server], block_migration=block_migration)
    server_steps.check_ping_to_server_floating(
        server, timeout=config.PING_CALL_TIMEOUT)

    stop_traffic()  # checker: disable
    server_steps.delete_servers([server])


@pytest.mark.idempotent_id('1fb54c78-20f5-459b-9515-3d7caf73ed64')
@pytest.mark.parametrize('block_migration', [True])
def test_migration_with_ephemeral_disk(
        keypair,
        security_group,
        floating_ip,
        cirros_image,
        net_subnet_router,
        create_flavor,
        server_steps,
        block_migration):
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
    #. Create flavor with ephemeral disk
    #. Boot server from cirros image with created flavor
    #. Assign floating ip to server
    #. Create timestamp on on root and ephemeral disks
    #. Migrate server to another hypervisor
    #. Start ping instance
    #. Check that pings reach the server succesfully
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
    flavor = create_flavor(
        next(generate_ids('flavor')), ram=64, disk=1, vcpus=1, ephemeral=1)

    server = server_steps.create_servers(image=cirros_image,
                                         flavor=flavor,
                                         keypair=keypair,
                                         networks=[net_subnet_router[0]],
                                         security_groups=[security_group],
                                         username=config.CIRROS_USERNAME)[0]

    server_steps.attach_floating_ip(server, floating_ip)
    timestamp = str(time.time())
    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.create_timestamps_on_root_and_ephemeral_disks(
            server_ssh, timestamp=timestamp)
    server_steps.live_migrate([server], block_migration=block_migration)
    server_steps.check_ping_to_server_floating(
        server, timeout=config.PING_CALL_TIMEOUT)
    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        server_steps.check_timestamps_on_root_and_ephemeral_disks(
            server_ssh, timestamp=timestamp)
