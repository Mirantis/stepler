"""
-----------------------------
Nova basic verification tests
-----------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('101ccfbf-5693-4d29-8878-296fea791a81')
def test_boot_instance_from_volume_bigger_than_flavor(
        flavor,
        security_group,
        nova_floating_ip,
        cirros_image,
        network,
        subnet,
        router,
        add_router_interfaces,
        volume_steps,
        server_steps):
    """**Scenario:** Boot instance from volume bigger than flavor size.

    This test verifies bug #1517671

    **Setup:**

    #. Upload cirros image
    #. Create network
    #. Create subnet
    #. Create router
    #. Create security group with allow ping rule
    #. Create flavor

    **Steps:**

    #. Set router default gateway to public network
    #. Add router interface to created network
    #. Create volume from cirros image with disk size bigger than flavor
    #. Boot server from volume
    #. Assign floating ip to server
    #. Check that ping to server's floating ip is successful

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
    volume_size = flavor.disk + 1

    volume = volume_steps.create_volumes(size=volume_size,
                                         image=cirros_image)[0]

    block_device_mapping = {'vda': volume.id}

    server = server_steps.create_servers(
        image=None,
        flavor=flavor,
        networks=[network],
        security_groups=[security_group],
        block_device_mapping=block_device_mapping)[0]

    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.check_ping_to_server_floating(server, timeout=5 * 60)


@pytest.mark.idempotent_id('9a75e111-c9dc-44e3-88fb-d315ae2deacb')
def test_delete_server_with_precreated_port(
        flavor,
        network,
        port,
        cirros_image,
        create_port,
        port_steps,
        server_steps):
    """**Scenario:** Delete instance with pre-created port.

    This test verifies bug #1486727

    **Setup:**

    #. Create flavor
    #. Create network
    #. Create subnet
    #. Upload cirros image
    #. Create port

    **Steps:**

    #. Boot server with created port
    #. Delete server
    #. Check that port is still present

    **Teardown:**

    #. Delete port
    #. Delete cirros image
    #. Delete network
    #. Delete subnet
    #. Delete flavor
    """
    servers = server_steps.create_servers(image=cirros_image,
                                          flavor=flavor,
                                          ports=[port])
    server_steps.delete_servers(servers)
    port_steps.check_presence(port)


@pytest.mark.idempotent_id('d8a8d247-3150-491a-b9e5-2f20cb0f384d')
def test_remove_incorrect_fixed_ip_from_server(
        server,
        nova_floating_ip,
        server_steps):
    """**Scenario:** [negative] Remove incorrect fixed IP from an instance.

    This test verifies bug #1534186
    https://bugs.launchpad.net/nova/+bug/1534186

    **Setup:**

    #. Create flavor
    #. Create security_group
    #. Create keypair
    #. Upload cirros image
    #. Create nova floating ip
    #. Boot server from cirros image

    **Steps:**

    #. Attach floating IP to server
    #. Generate fake IP
    #. Try to detach non-present fixed IP from server
    #. Check that error has been raised
    #. Detach present fixed IP from server
    #. Check that it will be detached with no error
    #. Check that server is accessible

    **Teardown:**

    #. Delete server
    #. Delete flavor
    #. Delete security group
    #. Delete keypair
    #. Delete cirros image
    #. Delete nova floating ip
    """
    server_steps.attach_floating_ip(server, nova_floating_ip)
    ip_fake = next(utils.generate_ips())

    server_steps.check_server_doesnot_detach_unattached_fixed_ip(
        server, ip_fake)
    server_steps.detach_fixed_ip(server)

    server_steps.get_server_ssh(server, ip=nova_floating_ip.ip)


@pytest.mark.idempotent_id('fc37666a-1438-4bcb-82e7-6cd782e9f8ac')
def test_delete_instance_during_resizing(cirros_image,
                                         network,
                                         subnet,
                                         create_flavor,
                                         server_steps,
                                         os_faults_steps):
    """**Scenario:** Verify that nova can delete servers in resize state.

    **Note:**
        This test verifies bug #1489775

    **Setup:**

    #. Upload cirros image
    #. Create network
    #. Create subnet

    **Steps:**

    #. Create 2 flavors
    #. Boot server with smaller flavor
    #. Resize server to bigger flavor
    #. Delete server immediately after its state will be 'RESIZE'
    #. Check that server's compute doesn't contains deleted server artifacts
    #. Repeat last 3 steps some times

    **Teardown:**

    #. Delete server
    #. Delete flavors
    #. Delete subnet
    #. Delete network
    #. Delete cirros image
    """
    small_flavor = create_flavor(
        next(utils.generate_ids('flavor-small')), ram=64, vcpus=1, disk=1)
    big_flavor = create_flavor(
        next(utils.generate_ids('flavor-big')), ram=128, vcpus=1, disk=2)

    for _ in range(10):
        server = server_steps.create_servers(
            count=1,
            image=cirros_image,
            networks=[network],
            flavor=small_flavor)[0]

        server_steps.resize(server, big_flavor, check=False)
        server_steps.check_server_status(
            server,
            [config.STATUS_RESIZE, config.STATUS_VERIFY_RESIZE],
            timeout=config.VERIFY_RESIZE_TIMEOUT)
        server_steps.delete_servers([server], soft=True)
        os_faults_steps.check_no_nova_server_artifacts(server)


@pytest.mark.idempotent_id('023648c3-8eee-4c91-8993-bb3999a86ab8')
def test_attach_detach_fixed_ip_to_server(
        flavor,
        security_group,
        keypair,
        cirros_image,
        net_subnet_router,
        nova_create_floating_ip,
        server_steps):
    """**Scenario:** Check server connectivity after attach/detach fixed IP.

    **Setup:**

    #. Create flavor
    #. Create security_group
    #. Create keypair
    #. Upload cirros image
    #. Create network with subnet and router

    **Steps:**

    #. Boot two servers from cirros image
    #. Create two nova floating ips
    #. Attach floating IP to each server
    #. Check that each server's IP address can be pinged from other server
    #. Attach new fixed IP to 1'st server
    #. Detach old fixed IP from 1'st server
    #. Check that new 1'st server's fixed IP can be pinged from 2'nd server.

    **Teardown:**

    #. Delete servers
    #. Delete flavor
    #. Delete security_group
    #. Delete keypair
    #. Delete cirros image
    #. Delete floating IPs
    #. Delete network, subnet, router
    """
    network, _, _ = net_subnet_router
    server_1, server_2 = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        keypair=keypair,
        security_groups=[security_group],
        username=config.CIRROS_USERNAME)

    server_1_float = nova_create_floating_ip()
    server_2_float = nova_create_floating_ip()

    server_steps.attach_floating_ip(server_1, server_1_float)
    server_steps.attach_floating_ip(server_2, server_2_float)

    server_steps.check_ping_between_servers_via_floating(
        [server_1, server_2], timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    old_fixed_ip = next(iter(server_steps.get_ips(server_1,
                                                  ip_type=config.FIXED_IP)))
    new_fixed_ip = server_steps.attach_fixed_ip(server_1, network['id'])
    server_steps.detach_fixed_ip(server_1, old_fixed_ip)

    # Reboot server to renew it's ip configuration (with DHCP)
    server_steps.reboot_server(server_1)

    with server_steps.get_server_ssh(server_2) as server_ssh:
        server_steps.check_ping_for_ip(
            new_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.idempotent_id('f46d5093-d2d6-4fc3-b9a1-9d9c9a2064db')
@pytest.mark.parametrize('volumes_count', [10])
def test_create_many_servers_boot_from_cinder(cirros_image,
                                              flavor,
                                              network,
                                              subnet,
                                              security_group,
                                              volume_steps,
                                              server_steps,
                                              volumes_count):
    """**Scenario:** Boot many servers from volumes.

    **Setup:**

    #. Upload cirros image
    #. Create flavor
    #. Create network
    #. Create subnet
    #. Create security group with allow ping rule

    **Steps:**

    #. Create 10 cinder volumes from cirros image
    #. Boot 10 servers from volumes

    **Teardown:**

    #. Delete servers
    #. Delete volumes
    #. Delete security group
    #. Delete subnet
    #. Delete network
    #. Delete flavor
    #. Delete cirros image
    """
    volumes = volume_steps.create_volumes(
        names=utils.generate_ids(count=volumes_count),
        image=cirros_image)

    for volume in volumes:
        block_device_mapping = {'vda': volume.id}
        server_steps.create_servers(
            image=None,
            flavor=flavor,
            networks=[network],
            security_groups=[security_group],
            block_device_mapping=block_device_mapping)


@pytest.mark.idempotent_id('4151cf32-9ffe-4cb2-bccb-a71aa8d993dc')
@pytest.mark.requires('nova_ceph')
@pytest.mark.usefixtures('disable_nova_use_cow_images')
def test_image_access_host_device_when_resizing(
        ubuntu_image,
        net_subnet_router,
        security_group,
        keypair,
        nova_floating_ip,
        create_flavor,
        server_steps):
    """**Scenario:** Resize server after unmounting fs.

    Test on host data leak during resize/migrate for raw-backed
    instances bug validation.
    This test verifies bugs #1552683 and #1548450 (CVE-2016-2140).

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Set router default gateway to public network
    #. Create security_group
    #. Create keypair
    #. Create nova floating ip

    **Steps:**

    #. Set use_cow_images=0 value in nova config on all computes
    #. Create 2 flavors with ephemeral disk
    #. Boot instance with the first flavor
    #. Create empty file in /mnt directory
    #. Unmount /mnt fs on the instance
    #. Create qcow2 image with backing_file linked to
        target host device in ephemeral block device on instance
        using the following command:
        ``qemu-img create -f qcow2
        -o backing_file=/dev/sda3,backing_fmt=raw /dev/vdb 20G``
    #. Resize flavor for the server
    #. Check that /mnt fs doesn't have files

    **Teardown:**

    #. Set use_cow_images param to its initial value on all computes
    #. Delete server
    #. Delete flavors
    #. Delete nova floating ip
    #. Delete keypair
    #. Delete security group
    #. Delete network
    #. Delete cirros image
    """
    eph_fs = config.EPHEMERAL_MNT_FS_PATH
    root_fs = config.EPHEMERAL_ROOT_FS_PATH
    image_size = config.DEFAULT_QCOW_IMAGE_SIZE

    network, _, _ = net_subnet_router

    flavor_old = create_flavor(
        next(utils.generate_ids('flavor')),
        ram=1024,
        disk=5,
        vcpus=1,
        ephemeral=1)
    flavor_new = create_flavor(
        next(utils.generate_ids('flavor')),
        ram=2048,
        disk=5,
        vcpus=1,
        ephemeral=1)

    server = server_steps.create_servers(
        image=ubuntu_image,
        flavor=flavor_old,
        keypair=keypair,
        networks=[network],
        security_groups=[security_group],
        username=config.UBUNTU_USERNAME,
        userdata=config.INSTALL_QEMU_UTILS_USERDATA)[0]
    # wait for userdata being installed
    server_steps.check_server_log_contains_record(
        server,
        config.USERDATA_DONE_MARKER,
        timeout=config.USERDATA_EXECUTING_TIMEOUT)

    server_steps.attach_floating_ip(server, nova_floating_ip)

    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
        # save names of devices before unmounting
        eph_dev = server_steps.get_block_device_by_mount(server_ssh, eph_fs)
        root_dev = server_steps.get_block_device_by_mount(server_ssh, root_fs)

        server_steps.create_empty_file_on_server(server_ssh, eph_fs)
        server_steps.unmount_fs_for_server(server_ssh, eph_fs)
        server_steps.create_qcow_image_for_server(server_ssh, eph_dev,
                                                  root_dev, image_size)

    server_steps.resize(server, flavor_new)
    server_steps.confirm_resize_servers([server])

    with server_steps.get_server_ssh(server,
                                     nova_floating_ip.ip) as server_ssh:
        server_steps.check_files_presence_for_fs(
            server_ssh, eph_fs, must_present=False)


@pytest.mark.requires('nova_ceph')
@pytest.mark.idempotent_id('98c0f75f-9e59-44c3-bd74-56760e3648bf')
def test_disk_io_qos_settings_for_rbd_backend(cirros_image,
                                              flavor,
                                              network,
                                              subnet,
                                              security_group,
                                              server_steps,
                                              flavor_steps,
                                              os_faults_steps):
    """**Scenario:** Check disk I/O QOS settings for RBD backend.

    This test verifies bug #1507504

    **Setup:**

    #. Upload cirros image
    #. Create flavor
    #. Create network
    #. Create subnet
    #. Create security group with allow ping rule

    **Steps:**

    #. Set I/O limits to flavor (disk_read_bytes_sec=10240000 and
       disk_write_bytes_sec=10240000)
    #. Create server
    #. Execute 'virsh dumpxml <inst_name>' on node where instance is hosted
    #. Check that its output contains read_bytes_sec and write_bytes_sec with
       expected values 10240000
    #. Execute 'ps axu | grep qemu | grep 'drive file=rbd' on node
    #. Check that its output contains 'bps_rd=10240000' and 'bps_wr=10240000'

    **Teardown:**

    #. Delete server
    #. Delete security group
    #. Delete subnet
    #. Delete network
    #. Delete flavor
    #. Delete cirros image
    """
    limit = config.IO_SPEC_LIMIT
    metadata = config.IO_SPEC_LIMIT_METADATA
    flavor_steps.set_metadata(flavor, metadata)

    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        security_groups=[security_group])[0]

    host_name = getattr(server, config.SERVER_ATTR_HOST)
    node = os_faults_steps.get_nodes(fqdns=[host_name])

    instance_name = getattr(server, config.SERVER_ATTR_INSTANCE_NAME)
    os_faults_steps.check_io_limits_in_virsh_dumpxml(node, instance_name,
                                                     limit)

    os_faults_steps.check_io_limits_in_ps(node, limit)


@pytest.mark.idempotent_id('acea91d1-6752-456d-99c2-fae6d873149c')
def test_create_delete_flavor(flavor_steps):
    """**Scenario:** Check flavor can be created and deleted.

    **Steps:**

    #. Create flavor
    #. Delete flavor
    """
    flavor = flavor_steps.create_flavor()
    flavor_steps.delete_flavor(flavor)


@pytest.mark.idempotent_id('2e4b036f-e17f-4688-b106-db2c3dd18779')
def test_flavors_list(flavor_steps):
    """**Scenario:** Request list of flavors.

    **Steps:**

    #. Get list of flavors
    """
    flavor_steps.get_flavors()


@pytest.mark.idempotent_id('b160b749-9894-4b06-90a4-4fecef371ae6')
def test_nova_services(os_faults_steps):
    """**Scenario:** Check that nova services are alive.

    **Steps:**

    #. Get list of nova services
    #. Check all services are running
    """
    nova_services = os_faults_steps.get_services_names(name_prefix='nova')
    for service in nova_services:
        nodes = os_faults_steps.get_nodes(service_names=[service])
        os_faults_steps.check_service_state(service, nodes=nodes)


@pytest.mark.idempotent_id('dc5fd8d1-7fb3-4c9e-a826-e4d4902ef260')
def test_create_delete_keypair(keypair):
    """**Scenario:** Check that keypair can be created and deleted.

    **Steps:**

    #. Create keypair
    #. Delete keypair
    """


@pytest.mark.idempotent_id('93654355-69b3-41c8-adfc-e3e7033789c7')
def test_instances_list(server_steps):
    """**Scenario:** Request list of instances.

    **Steps:**

    #. Get list of instances
    """
    server_steps.get_servers(check=False)


@pytest.mark.idempotent_id('b8d7c80c-0c29-42f9-b14d-bc5f5fb3e969')
def test_absolute_limits_list(nova_limit_steps):
    """**Scenario:** Request list of absolute limits.

    **Steps:**

    #. Get list of absolute limits
    """
    nova_limit_steps.get_absolute_limits()
