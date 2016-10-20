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

from stepler import config
from stepler.third_party.utils import generate_ids


def test_restore_deleted_instance(
        modify_config_file_with_services_restart, cirros_image, flavor,
        network, subnet, keypair, security_group, router,
        add_router_interfaces, create_server, nova_create_floating_ip,
        create_volume, attach_volume_to_server,
        server_steps, os_faults_steps):
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
    reclaim_interval = 24 * 60 * 60
    service_names = ['nova-api', 'nova-compute']
    nodes = os_faults_steps.get_nodes(service_names=service_names)
    modify_config_file_with_services_restart(
        nodes, path='/etc/nova/nova.conf', option='reclaim_instance_interval',
        value=str(reclaim_interval), service_names=service_names)

    add_router_interfaces(router, [subnet])
    server1 = create_server(next(generate_ids('server')),
                            image=cirros_image,
                            flavor=flavor,
                            networks=[network],
                            keypair=keypair,
                            security_groups=[security_group],
                            username='cirros')
    floating_ip1 = nova_create_floating_ip()
    server_steps.attach_floating_ip(server1, floating_ip1)
    server_steps.check_ping_to_server_floating(
        server1, timeout=config.PING_CALL_TIMEOUT)

    server2 = create_server(server_name=next(generate_ids('server')),
                            image=cirros_image,
                            flavor=flavor,
                            networks=[network],
                            keypair=keypair,
                            security_groups=[security_group],
                            username='cirros')
    floating_ip2 = nova_create_floating_ip()
    server_steps.attach_floating_ip(server2, floating_ip2)
    server_steps.check_ping_to_server_floating(
        server2, timeout=config.PING_CALL_TIMEOUT)

    server_steps.check_ping_between_servers_via_floating(
        [server1, server2], timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    volume = create_volume(next(generate_ids('volume')))
    attach_volume_to_server(server1, volume)

    server_steps.delete_server(server1, force=False, soft=True)

    server_steps.restore_server(server1)
    server_steps.check_ping_to_server_floating(
        server1, timeout=config.PING_CALL_TIMEOUT)

    server_steps.check_ping_between_servers_via_floating(
        [server1, server2], timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


def test_inst_deleted_reclaim_interval_timeout(
        modify_config_file_with_services_restart, cirros_image, flavor,
        network, subnet, keypair, security_group, create_server,
        create_volume, attach_volume_to_server, detach_volume_from_server,
        server_steps, cinder_steps, os_faults_steps):
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
    reclaim_interval = 30
    service_names = ['nova-api', 'nova-compute']
    nodes = os_faults_steps.get_nodes(service_names=service_names)
    modify_config_file_with_services_restart(
        nodes, path='/etc/nova/nova.conf', option='reclaim_instance_interval',
        value=str(reclaim_interval), service_names=service_names)

    server1 = create_server(next(generate_ids('server')),
                            image=cirros_image,
                            flavor=flavor,
                            networks=[network],
                            keypair=keypair,
                            security_groups=[security_group],
                            username='cirros')

    server2 = create_server(server_name=next(generate_ids('server')),
                            image=cirros_image,
                            flavor=flavor,
                            networks=[network],
                            keypair=keypair,
                            security_groups=[security_group],
                            username='cirros')

    volume = create_volume(next(generate_ids('volume')))

    attach_volume_to_server(server1, volume)

    server_steps.delete_server(server1, force=False, soft=True)

    # TODO(ssokolov) workaround for bug 1463856
    detach_volume_from_server(server1, volume)

    server_steps.check_server_presence(server1, present=False,
                                       timeout=reclaim_interval * 3)

    cinder_steps.check_volume_status(volume, 'available',
                                     timeout=config.VOLUME_AVAILABLE_TIMEOUT)
    cinder_steps.check_volume_attachments(volume, [])

    attach_volume_to_server(server2, volume)
    detach_volume_from_server(server2, volume)


def test_force_delete_inst_before_deferred_cleanup(
        modify_config_file_with_services_restart, cirros_image, flavor,
        network, subnet, keypair, security_group, create_server,
        create_volume, attach_volume_to_server, detach_volume_from_server,
        server_steps, cinder_steps, os_faults_steps):
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
    reclaim_interval = 24 * 60 * 60
    service_names = ['nova-api', 'nova-compute']
    nodes = os_faults_steps.get_nodes(service_names=service_names)
    modify_config_file_with_services_restart(
        nodes, path='/etc/nova/nova.conf', option='reclaim_instance_interval',
        value=str(reclaim_interval), service_names=service_names)

    server1 = create_server(next(generate_ids('server')),
                            image=cirros_image,
                            flavor=flavor,
                            networks=[network],
                            keypair=keypair,
                            security_groups=[security_group],
                            username='cirros')

    server2 = create_server(server_name=next(generate_ids('server')),
                            image=cirros_image,
                            flavor=flavor,
                            networks=[network],
                            keypair=keypair,
                            security_groups=[security_group],
                            username='cirros')

    volume = create_volume(next(generate_ids('volume')))
    attach_volume_to_server(server1, volume)

    server_steps.delete_server(server1, force=False, soft=True)

    server_steps.delete_server(server1, force=True)
    cinder_steps.check_volume_status(volume, 'available',
                                     timeout=config.VOLUME_AVAILABLE_TIMEOUT)
    cinder_steps.check_volume_attachments(volume, [])

    attach_volume_to_server(server2, volume)
    detach_volume_from_server(server2, volume)
