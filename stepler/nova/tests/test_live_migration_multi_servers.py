"""
---------------------------------------------
Nova live migration of multiple servers tests
---------------------------------------------
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


import pytest

from stepler import config

pytestmark = [
    pytest.mark.usefixtures('skip_live_migration_tests',
                            'disable_nova_config_drive',
                            'unlimited_live_migrations'),
    pytest.mark.requires('computes_count >= 2')
]


@pytest.mark.idempotent_id('78dcde62-39fd-4913-827e-99294d6ca983',
                           block_migration=True)
@pytest.mark.idempotent_id('9c6b94cb-959f-4d7f-9e7a-f7dff667ca6f',
                           block_migration=False)
@pytest.mark.parametrize(
    'live_migration_servers, block_migration', [
        ({'boot_from_volume': False}, True),
        ({'boot_from_volume': True}, False)
    ],
    ids=['boot_from_image', 'boot_from_volume'],
    indirect=['live_migration_servers'])
@pytest.mark.destructive
def test_migration_with_memory_workload(live_migration_servers,
                                        server_steps,
                                        block_migration):
    """**Scenario:** LM of servers under memory workload.

    **Setup:**

    #. Upload ubuntu image
    #. Create network with subnet and router
    #. Create security group with allow ping rule
    #. Create flavor
    #. Boot maximum allowed number of servers from image or volume
    #. Assign floating ips to servers

    **Steps:**

    #. Start memory workload on servers
    #. Initiate LM of servers to another compute node
    #. Check that ping to servers' floating ips is successful
    #. Delete servers

    **Teardown:**

    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete ubuntu image
    """
    for server in live_migration_servers:
        with server_steps.get_server_ssh(server) as server_ssh:
            server_steps.generate_server_memory_workload(server_ssh)

    server_steps.live_migrate(live_migration_servers,
                              block_migration=block_migration)

    for server in live_migration_servers:
        server_steps.check_ping_to_server_floating(
            server, timeout=config.PING_CALL_TIMEOUT)

    server_steps.delete_servers(live_migration_servers)


@pytest.mark.idempotent_id('b0b0baa4-60af-4429-98f2-eb137eae8219',
                           block_migration=True)
@pytest.mark.idempotent_id('70ed751c-abe6-48f0-a785-f756b04a4ca7',
                           block_migration=False)
@pytest.mark.parametrize(
    'live_migration_servers, block_migration', [
        ({'boot_from_volume': False}, True),
        ({'boot_from_volume': True}, False)],
    ids=['boot_from_image', 'boot_from_volume'],
    indirect=['live_migration_servers'])
@pytest.mark.destructive
def test_migration_with_cpu_workload(live_migration_servers,
                                     server_steps,
                                     block_migration):
    """**Scenario:** LM of servers under CPU workload.

    **Setup:**

    #. Upload ubuntu image
    #. Create network with subnet and router
    #. Create security group with allow ping rule
    #. Create flavor
    #. Boot maximum allowed number of servers from image or volume
    #. Assign floating ips to servers

    **Steps:**

    #. Start CPU workload on servers
    #. Initiate LM of servers to another compute node
    #. Check that ping to servers' floating ips is successful
    #. Delete servers

    **Teardown:**

    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete ubuntu image
    """
    for server in live_migration_servers:
        with server_steps.get_server_ssh(server) as server_ssh:
            server_steps.generate_server_cpu_workload(server_ssh)

    server_steps.live_migrate(live_migration_servers,
                              block_migration=block_migration)
    for server in live_migration_servers:
        server_steps.check_ping_to_server_floating(
            server, timeout=config.PING_CALL_TIMEOUT)

    server_steps.delete_servers(live_migration_servers)


@pytest.mark.idempotent_id('77dcf03f-20d3-4d71-96f5-8fb1343f906a')
@pytest.mark.parametrize('block_migration', [True])
@pytest.mark.destructive
def test_migration_with_disk_workload(live_migration_servers,
                                      server_steps,
                                      block_migration):
    """**Scenario:** Block LM of servers under disk workload.

    **Setup:**

    #. Upload ubuntu image
    #. Create network with subnet and router
    #. Create security group with allow ping rule
    #. Create flavor
    #. Boot maximum allowed number of servers from image
    #. Assign floating ips to servers

    **Steps:**

    #. Start disk workload on servers
    #. Initiate LM of servers to another compute node
    #. Check that ping to servers' floating ips is successful
    #. Delete servers

    **Teardown:**

    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete ubuntu image
    """

    for server in live_migration_servers:
        with server_steps.get_server_ssh(server) as server_ssh:
            server_steps.generate_server_disk_workload(server_ssh)

    server_steps.live_migrate(live_migration_servers,
                              block_migration=block_migration)
    for server in live_migration_servers:
        server_steps.check_ping_to_server_floating(
            server, timeout=config.PING_CALL_TIMEOUT)

    server_steps.delete_servers(live_migration_servers)


@pytest.mark.idempotent_id('b1152b92-5021-4115-9b89-c423fd61abad',
                           block_migration=True)
@pytest.mark.idempotent_id('233c1cf6-de63-4a90-b151-c94f1faa276f',
                           block_migration=False)
@pytest.mark.parametrize(
    'live_migration_servers, block_migration', [
        ({'boot_from_volume': False}, True),
        ({'boot_from_volume': True}, False)],
    ids=['boot_from_image', 'boot_from_volume'],
    indirect=['live_migration_servers'])
@pytest.mark.destructive
def test_migration_with_network_workload(
        live_migration_servers,
        security_group,
        generate_traffic,
        neutron_security_group_rule_steps,
        server_steps,
        block_migration):
    """**Scenario:** LM of servers under network workload.

    **Setup:**

    #. Upload ubuntu image
    #. Create network with subnet and router
    #. Create security group with allow ping rule
    #. Create flavor
    #. Boot maximum allowed number of servers from image or volume
    #. Assign floating ips to servers

    **Steps:**

    #. Allow servers to listen TCP port
    #. Start network workload on servers
    #. Initiate LM of servers to another compute node
    #. Check that ping to servers' floating ips is successful
    #. Delete servers

    **Teardown:**

    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete ubuntu image
    """

    port = 5010
    neutron_security_group_rule_steps.add_rule_to_group(
        security_group['id'],
        direction=config.INGRESS,
        protocol='tcp',
        port_range_min=port,
        port_range_max=port,
        remote_ip_prefix='0.0.0.0/0')

    for server in live_migration_servers:
        with server_steps.get_server_ssh(server) as server_ssh:
            server_steps.server_network_listen(server_ssh, port=port)
            floating_ip = server_steps.get_floating_ip(server)
            generate_traffic(floating_ip, port)

    server_steps.live_migrate(live_migration_servers,
                              block_migration=block_migration)
    for server in live_migration_servers:
        server_steps.check_ping_to_server_floating(
            server, timeout=config.PING_CALL_TIMEOUT)

    server_steps.delete_servers(live_migration_servers)


@pytest.mark.idempotent_id('00495cbf-7476-4143-91fc-37e23626d548',
                           block_migration=True)
@pytest.mark.idempotent_id('fdcec5a2-75d8-4f76-ae28-aba865c6e778',
                           block_migration=False)
@pytest.mark.parametrize(
    'live_migration_servers, block_migration', [
        (dict(boot_from_volume=False, attach_volume=True), True),
        (dict(boot_from_volume=True, attach_volume=True), False)
    ],
    ids=['boot_from_image', 'boot_from_volume'],
    indirect=['live_migration_servers'])
def test_migration_with_attached_volume(live_migration_servers_with_volumes,
                                        server_steps,
                                        block_migration):
    """**Scenario:** LM of servers with attached volumes.

    **Setup:**

    #. Upload ubuntu image
    #. Create network with subnet and router
    #. Create security group with allow ping rule
    #. Create flavor
    #. Boot maximum allowed number of servers from image or volume
    #. Attach volume to each server
    #. Assign floating ips to servers

    **Steps:**

    #. Initiate LM of servers to another compute node
    #. Check that ping to servers' floating ips is successful

    **Teardown:**

    #. Delete servers
    #. Delete volumes
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete ubuntu image
    """
    server_steps.live_migrate(
        live_migration_servers_with_volumes, block_migration=block_migration)
    for server in live_migration_servers_with_volumes:
        server_steps.check_ping_to_server_floating(
            server, timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.idempotent_id('f2ac5153-21ee-4a99-869a-d0a78af124c8',
                           flavor=dict(ram=16 * 1024, vcpus=8, disk=160),
                           block_migration=True)
@pytest.mark.idempotent_id('923cf57b-bcd2-4b1b-a6f4-9656036e11e4',
                           flavor=dict(ram=16 * 1024, vcpus=8, disk=160),
                           block_migration=False)
@pytest.mark.idempotent_id('8e588cf2-a2db-4ad5-a7e5-6dc8f5612d31',
                           flavor=dict(ram=8 * 1024, vcpus=4, disk=80),
                           block_migration=True)
@pytest.mark.idempotent_id('7abf7397-d2de-4b8e-a4cb-52e238842c14',
                           flavor=dict(ram=8 * 1024, vcpus=4, disk=80),
                           block_migration=False)
@pytest.mark.parametrize(
    'flavor', [
        dict(ram=16 * 1024, vcpus=8, disk=160),
        dict(ram=8 * 1024, vcpus=4, disk=80),
    ],
    indirect=True)
@pytest.mark.parametrize(
    'live_migration_servers, block_migration',
    [(dict(boot_from_volume=True), False),
     (dict(boot_from_volume=False), True)],
    indirect=['live_migration_servers'])
def test_migration_with_large_flavors(live_migration_servers,
                                      server_steps,
                                      block_migration):
    """**Scenario:** LM of servers with attached volumes.

    **Setup:**

    #. Upload ubuntu image
    #. Create network with subnet and router
    #. Create security group with allow ping rule
    #. Create flavor
    #. Boot maximum allowed number of servers from image or volume
    #. Attach volume to each server
    #. Assign floating ips to servers

    **Steps:**

    #. Initiate LM of servers to another compute node
    #. Check that ping to servers' floating ips is successful

    **Teardown:**

    #. Delete servers
    #. Delete volumes
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete ubuntu image
    """
    server_steps.live_migrate(
        live_migration_servers, block_migration=block_migration)
    for server in live_migration_servers:
        server_steps.check_ping_to_server_floating(
            server, timeout=config.PING_CALL_TIMEOUT)
