"""
--------------------------
Nova deferred delete tests
--------------------------
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

NOVA_SERVICES = [config.NOVA_API, config.NOVA_COMPUTE]


@pytest.mark.idempotent_id('c80af877-bf63-4b1c-bcc4-14571da1d971')
def test_restore_soft_deleted_server(
        cirros_image,
        flavor,
        network,
        subnet,
        keypair,
        security_group,
        router,
        patch_ini_file_and_restart_services,
        add_router_interfaces,
        nova_create_floating_ip,
        attach_volume_to_server,
        volume_steps,
        server_steps):
    """**Scenario:** Restore previously deleted instance

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create net and subnet
    #. Create keypair
    #. Create security group
    #. Create router

    **Steps:**

    #. Update /etc/nova/nova.conf with 'reclaim_instance_interval=86400'
       and restart nova-api and nova-compute on all nodes
    #. Add router interface
    #. Create and run two instances (vm1, vm2) inside same net
    #. Create and attach floating IPs to instances
    #. Check that ping are successful between vms
    #. Create a volume and attach it to an instance vm1
    #. Delete instance vm1 and check that it's in 'SOFT_DELETE' state
    #. Restore vm1 instance and check that it's in 'ACTIVE' state
    #. Check that ping are successful between vms

    **Teardown:**

    #. Delete volume
    #. Delete vms
    #. Delete router and router interface
    #. Delete security group
    #. Delete keypair
    #. Delete net and subnet
    #. Delete flavor
    #. Delete cirros image
    #. Restore original config files and restart nova-api and
       nova-compute on all nodes
    """
    with patch_ini_file_and_restart_services(
            NOVA_SERVICES,
            path=config.NOVA_CONFIG_PATH,
            option='reclaim_instance_interval',
            value=config.BIG_RECLAIM_INTERVAL):

        add_router_interfaces(router, [subnet])

        server_1 = server_steps.create_servers(
            server_names=utils.generate_ids('server', count=1),
            image=cirros_image,
            flavor=flavor,
            networks=[network],
            keypair=keypair,
            security_groups=[security_group],
            username=config.CIRROS_USERNAME)[0]

        floating_ip_1 = nova_create_floating_ip()
        server_steps.attach_floating_ip(server_1, floating_ip_1)
        server_steps.check_ping_to_server_floating(
            server_1, timeout=config.PING_CALL_TIMEOUT)

        server_2 = server_steps.create_servers(
            server_names=utils.generate_ids('server', count=1),
            image=cirros_image,
            flavor=flavor,
            networks=[network],
            keypair=keypair,
            security_groups=[security_group],
            username=config.CIRROS_USERNAME)[0]

        floating_ip_2 = nova_create_floating_ip()
        server_steps.attach_floating_ip(server_2, floating_ip_2)
        server_steps.check_ping_to_server_floating(
            server_2, timeout=config.PING_CALL_TIMEOUT)

        server_steps.check_ping_between_servers_via_floating(
            [server_1, server_2], timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

        volume = volume_steps.create_volumes(
            names=utils.generate_ids('volume', count=1))[0]
        attach_volume_to_server(server_1, volume)

        server_steps.delete_servers([server_1], soft=True)
        server_steps.restore_server(server_1)

        server_steps.check_ping_to_server_floating(
            server_1, timeout=config.PING_CALL_TIMEOUT)

        server_steps.check_ping_between_servers_via_floating(
            [server_1, server_2], timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.idempotent_id('2498c8dd-a48e-4044-8c14-6d5d603e6f0b')
def test_server_deleted_after_reclaim_timeout(
        cirros_image,
        flavor,
        network,
        subnet,
        keypair,
        security_group,
        router,
        patch_ini_file_and_restart_services,
        add_router_interfaces,
        attach_volume_to_server,
        detach_volume_from_server,
        server_steps,
        volume_steps):
    """**Scenario:** Check that softly-deleted instance is totally deleted
    after reclaim interval timeout.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create net and subnet
    #. Create keypair
    #. Create security group
    #. Create router

    **Steps:**

    #. Update '/etc/nova/nova.conf' with 'reclaim_instance_interval=30'
       and restart nova-api and nova-compute on all nodes
    #. Create and run two instances (vm1, vm2) inside same net
    #. Create and attach floating IPs to instances
    #. Check that ping are successful between vms
    #. Create a volume and attach it to an instance vm1
    #. Delete instance vm1 and check that it's in 'SOFT_DELETE' state
    #. Wait for the reclaim instance interval to expire and make sure
       that vm1 is deleted
    #. Check that volume is released now and has an Available state
    #. Attach the volume to vm2 and check that it has 'in-use' state.
    #. Detach the volume

    **Teardown:**

    #. Delete volume
    #. Delete vms
    #. Delete security group
    #. Delete keypair
    #. Delete net and subnet
    #. Delete flavor
    #. Delete cirros image
    #. Restore original config files and restart nova-api and
       nova-compute on all nodes

    ~! BUG !~
    https://bugs.launchpad.net/cinder/+bug/1463856
    Cinder volume isn't available after instance soft-deleted timer
    expired while volume is still attached.
    """
    with patch_ini_file_and_restart_services(
            NOVA_SERVICES,
            path=config.NOVA_CONFIG_PATH,
            option='reclaim_instance_interval',
            value=config.SMALL_RECLAIM_INTERVAL):

        add_router_interfaces(router, [subnet])

        server_1 = server_steps.create_servers(
            server_names=utils.generate_ids('server', count=1),
            image=cirros_image,
            flavor=flavor,
            networks=[network],
            keypair=keypair,
            security_groups=[security_group],
            username=config.CIRROS_USERNAME)[0]

        server_2 = server_steps.create_servers(
            server_names=utils.generate_ids('server', count=1),
            image=cirros_image,
            flavor=flavor,
            networks=[network],
            keypair=keypair,
            security_groups=[security_group],
            username=config.CIRROS_USERNAME)[0]

        volume = volume_steps.create_volumes(
            names=utils.generate_ids('volume', count=1))[0]

        attach_volume_to_server(server_1, volume)
        server_steps.delete_servers([server_1], soft=True)

        # TODO(ssokolov) workaround for bug
        # https://bugs.launchpad.net/nova/+bug/1463856
        detach_volume_from_server(server_1, volume)

        server_steps.check_server_presence(
            server_1, present=False, timeout=config.SMALL_RECLAIM_TIMEOUT)

        volume_steps.check_volume_status(
            volume, config.STATUS_AVAILABLE,
            timeout=config.VOLUME_AVAILABLE_TIMEOUT)
        volume_steps.check_volume_attachments(volume, server_ids=None)

        attach_volume_to_server(server_2, volume)
        detach_volume_from_server(server_2, volume)


@pytest.mark.idempotent_id('25c0b19e-e58d-4c74-9c8c-dd5f4e9a2b99')
def test_force_delete_server_before_deferred_cleanup(
        cirros_image,
        flavor,
        network,
        subnet,
        keypair,
        security_group,
        router,
        patch_ini_file_and_restart_services,
        add_router_interfaces,
        create_server_context,
        attach_volume_to_server,
        detach_volume_from_server,
        server_steps,
        volume_steps):
    """**Scenario:** Force delete of instance before deferred cleanup

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create net and subnet
    #. Create keypair
    #. Create security group
    #. Create router

    **Steps:**

    #. Update /etc/nova/nova.conf with 'reclaim_instance_interval=86400'
       and restart nova-api and nova-compute on all nodes
    #. Create and run two instances (vm1, vm2) inside same net
    #. Create a volume and attach it to an instance vm1
    #. Delete instance vm1 and check that it's in 'SOFT_DELETE' state
    #. Delete instance vm1 with 'force' option and check that it's not
       present.
    #. Check that volume is released now and has an Available state;
    #. Attach the volume to vm2 and check that it has 'in-use' state.
    #. Detach the volume

    **Teardown:**

    #. Delete volume
    #. Delete vms
    #. Delete security group
    #. Delete keypair
    #. Delete net and subnet
    #. Delete flavor
    #. Delete cirros image
    #. Restore original config files and restart nova-api and
       nova-compute on all nodes
    """
    with patch_ini_file_and_restart_services(
            NOVA_SERVICES,
            path=config.NOVA_CONFIG_PATH,
            option='reclaim_instance_interval',
            value=config.BIG_RECLAIM_INTERVAL):

        add_router_interfaces(router, [subnet])

        server_name_1 = next(utils.generate_ids('server'))
        with create_server_context(
                server_name_1,
                image=cirros_image,
                flavor=flavor,
                networks=[network],
                keypair=keypair,
                security_groups=[security_group],
                username=config.CIRROS_USERNAME) as server_1:

            server_2 = server_steps.create_servers(
                server_names=utils.generate_ids('server', count=1),
                image=cirros_image,
                flavor=flavor,
                networks=[network],
                keypair=keypair,
                security_groups=[security_group],
                username=config.CIRROS_USERNAME)[0]

            volume = volume_steps.create_volumes(
                names=utils.generate_ids('volume', count=1))[0]
            attach_volume_to_server(server_1, volume)

            server_steps.delete_servers([server_1], soft=True)

        volume_steps.check_volume_status(
            volume, config.STATUS_AVAILABLE,
            timeout=config.VOLUME_AVAILABLE_TIMEOUT)
        volume_steps.check_volume_attachments(volume, server_ids=None)

        attach_volume_to_server(server_2, volume)
        detach_volume_from_server(server_2, volume)
