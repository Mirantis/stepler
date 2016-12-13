"""
--------------------
Cinder service tests
--------------------
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
from stepler.third_party import utils

pytestmark = pytest.mark.destructive


@pytest.mark.idempotent_id('e3a64b34-fbc3-4b96-a123-78516b7b054c')
def test_restart_all_cinder_services(volume,
                                     server,
                                     nova_floating_ip,
                                     attach_volume_to_server,
                                     os_faults_steps,
                                     server_steps,
                                     volume_steps):
    """**Scenario:** Cinder services work after restart.

    **Setup:**

    #. Create volume
    #. Create ubuntu server
    #. Create floating IP

    **Steps:**

    #. Attach floating IP to ubuntu server
    #. Check server is pinged via floating IP
    #. Attach volume to ubuntu server
    #. Mount volume inside ubuntu server
    #. Create empty file inside volume
    #. Restart cinder services
    #. Check cinder services are available
    #. Create volume_2
    #. Attache volume_2 to ubuntu server
    #. Mount volume_2 inside ubuntu server
    #. Copy empty file from volume to volume_2

    **Teardown:**

    #. Detach volumes from ubuntu server
    #. Delete floating IP
    #. Delete ubuntu server
    #. Delete created volumes
    """
    device_1, device_2 = '/dev/vdc', '/dev/vdd'
    folder_1, folder_2 = '/mnt/volume_1', '/mnt/volume_2'
    file_name = next(utils.generate_ids())

    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.check_ping_to_server_floating(
        server, timeout=config.PING_CALL_TIMEOUT)

    attach_volume_to_server(server, volume, device=device_1)

    server_steps.execute_commands(
        server,
        ['{} mkfs.ext2 {}'.format(config.CIRROS_ENV_PATH, device_1),
         'mkdir {}'.format(folder_1),
         'mount {} {}'.format(device_1, folder_1),
         'touch {}/{}'.format(folder_1, file_name)],
        with_sudo=True)

    os_faults_steps.restart_services(config.CINDER_SERVICES)
    volume_steps.check_cinder_available()

    volume_2 = volume_steps.create_volumes()[0]
    attach_volume_to_server(server, volume_2, device=device_2)

    server_steps.execute_commands(
        server,
        ['{} mkfs.ext2 {}'.format(config.CIRROS_ENV_PATH, device_2),
         'mkdir {}'.format(folder_2),
         'mount {} {}'.format(device_2, folder_2),
         'cp {0}/{2} {1}/{2}'.format(folder_1, folder_2, file_name)],
        with_sudo=True)


@pytest.mark.idempotent_id('5c9b82f6-4a4e-4118-bf67-7a69718c61db')
def test_stop_nova_and_cinder_services(server,
                                       nova_floating_ip,
                                       attach_volume_to_server,
                                       detach_volume_from_server,
                                       server_steps,
                                       volume_steps,
                                       os_faults_steps):
    """**Scenario:** VM with volume is available if nova and cinder disabled.

    **Setup:**

    #. Create ubuntu server
    #. Create floating IP

    **Steps:**

    #. Attach floating IP to ubuntu server
    #. Check ubuntu server is pinged with floating IP
    #. Create volume with size 10 Gb
    #. Attach volume to ubuntu server
    #. Via SSH create file on attached volume
    #. Stop cinder-volume service
    #. Stop nova-compute service
    #. Via SSH copy file on attached volume and check that it's the same
    #. Start nova-compute service
    #. Start cinder-volume service
    #. Detach volume from ubuntu server

    **Teardown:**

    #. Delete volume
    #. Delete floating IP
    #. Delete ubuntu server
    """
    device = '/dev/vdc'
    folder = '/mnt/volume'
    file_name_1, file_name_2 = utils.generate_ids(count=2)

    server_steps.attach_floating_ip(server, nova_floating_ip)

    server_steps.check_ping_to_server_floating(
        server, timeout=config.PING_CALL_TIMEOUT)

    volume = volume_steps.create_volumes(size=10)[0]
    attach_volume_to_server(server, volume, device=device)

    server_steps.execute_commands(
        server,
        ['{} mkfs.ext2 {}'.format(config.CIRROS_ENV_PATH, device),
         'mkdir {}'.format(folder),
         'mount {} {}'.format(device, folder),
         'echo "test" > {}/{}'.format(folder, file_name_1)],
        with_sudo=True)

    cinder_nodes = os_faults_steps.get_nodes(
        service_names=[config.CINDER_VOLUME])

    nova_nodes = os_faults_steps.get_nodes(
        service_names=[config.NOVA_COMPUTE])

    os_faults_steps.terminate_service(config.CINDER_VOLUME, cinder_nodes)
    os_faults_steps.terminate_service(config.NOVA_COMPUTE, nova_nodes)

    server_steps.execute_commands(
        server,
        ['cp {0}/{1} {0}/{2}'.format(folder, file_name_1, file_name_2),
         'diff {0}/{1} {0}/{2}'.format(folder, file_name_1, file_name_2)],
        with_sudo=True)

    os_faults_steps.start_service(config.NOVA_COMPUTE, nova_nodes)
    os_faults_steps.start_service(config.CINDER_VOLUME, cinder_nodes)

    detach_volume_from_server(server, volume)
