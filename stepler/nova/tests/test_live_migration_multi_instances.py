"""
-----------------------------------------------
Nova live migration of multiple instances tests
-----------------------------------------------
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
    pytest.mark.requires('computes_count_gte(2)')
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
def test_server_migration_with_memory_workload(live_migration_servers,
                                               server_steps,
                                               block_migration):
    """**Scenario:** LM of instances under memory workload.

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

    **Teardown:**

    #. Delete servers
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
def test_server_migration_with_cpu_workload(live_migration_servers,
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

    **Teardown:**

    #. Delete servers
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


@pytest.mark.idempotent_id('77dcf03f-20d3-4d71-96f5-8fb1343f906a')
@pytest.mark.parametrize('block_migration', [True])
def test_server_migration_with_disk_workload(live_migration_servers,
                                             server_steps,
                                             block_migration):
    """**Scenario:** LM of instance under disk workload.

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

    **Teardown:**

    #. Delete servers
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
