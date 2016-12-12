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


@pytest.mark.idempotent_id('85adec8d-bf7c-41a7-ba0f-818d39410cfe')
def test_restart_all_cinder_services(volume,
                                     ubuntu_server,
                                     nova_floating_ip,
                                     attach_volume_to_server,
                                     get_ssh_proxy_cmd,
                                     os_faults_steps,
                                     server_steps,
                                     volume_steps):
    """**Scenario:** Check that cinder works after restarting services.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create keypair
    #. Create network with subnet and router
    #. Create security group
    #. Create server_1

    **Steps:**

    #. Check that ping from server_1 to 8.8.8.8 is successful
    #. Create image_1 and check its content
    #. Restart glance services
    #. Wait for glance service availability
    #. Check that image_1 is in images list and its content is expected as well
    #. Create image_2 and check its content
    #. Create server_2 and check ping to 8.8.8.8 from it

    **Teardown:**

    #. Delete images
    #. Delete servers
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete keypair
    #. Delete flavor
    #. Delete cirros image
    """
    server_steps.attach_floating_ip(ubuntu_server, nova_floating_ip)
    server_steps.check_ping_to_server_floating(
        ubuntu_server, timeout=config.PING_CALL_TIMEOUT)

    attach_volume_to_server(ubuntu_server, volume, device='/dev/vdc')

    server_steps.execute_commands(ubuntu_server,
                                  ['sudo mkfs -t ext3 /dev/vdc',
                                   'sudo mkdir /mnt/volume_1',
                                   'sudo mount /dev/vdc /mnt/volume_1',
                                   'sudo touch /mnt/volume_1/test_file'])

    os_faults_steps.restart_services(config.CINDER_SERVICES)
    volume_steps.check_cinder_available()

    volume_2 = volume_steps.create_volumes()[0]
    attach_volume_to_server(ubuntu_server, volume_2, device='/dev/vdd')

    server_steps.execute_commands(
        ubuntu_server,
        ['sudo mkfs -t ext3 /dev/vdd',
         'sudo mkdir /mnt/volume_2',
         'sudo mount /dev/vdd /mnt/volume_2',
         'sudo cp /mnt/volume_1/test_file /mnt/volume_1/test_file'])
