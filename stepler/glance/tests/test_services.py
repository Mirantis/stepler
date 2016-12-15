"""
--------------------
Glance service tests
--------------------
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

pytestmark = pytest.mark.destructive


@pytest.mark.idempotent_id('85adec8d-bf7c-41a7-ba0f-818d39410cfe')
def test_restart_all_glance_services(cirros_image,
                                     flavor,
                                     keypair,
                                     net_subnet_router,
                                     security_group,
                                     server,
                                     get_ssh_proxy_cmd,
                                     glance_steps,
                                     os_faults_steps,
                                     server_steps):
    """**Scenario:** Check that glance works after restarting services.

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
    proxy_cmd = get_ssh_proxy_cmd(server)
    with server_steps.get_server_ssh(
            server, proxy_cmd=proxy_cmd) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP, server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)

    file_path_1 = next(utils.generate_files())
    image_1 = glance_steps.create_images(image_path=file_path_1)[0]
    glance_steps.check_image_data_corresponds_to_source(image_1, file_path_1)

    os_faults_steps.restart_services(config.GLANCE_SERVICES)
    glance_steps.check_glance_service_available()

    glance_steps.check_image_presence(image_1)
    glance_steps.check_image_data_corresponds_to_source(image_1, file_path_1)

    file_path_2 = next(utils.generate_files())
    image_2 = glance_steps.create_images(image_path=file_path_2)[0]
    glance_steps.check_image_data_corresponds_to_source(image_2, file_path_2)

    server_2 = server_steps.create_servers(image=cirros_image,
                                           flavor=flavor,
                                           networks=[net_subnet_router[0]],
                                           keypair=keypair,
                                           security_groups=[security_group],
                                           username=config.CIRROS_USERNAME)[0]
    proxy_cmd = get_ssh_proxy_cmd(server_2)
    with server_steps.get_server_ssh(
            server_2, proxy_cmd=proxy_cmd) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP, server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)


@pytest.mark.idempotent_id("683bd20b-4adc-4a51-a855-f4950acd782f",
                           controller_cmd=config.FUEL_PRIMARY_CONTROLLER_CMD)
@pytest.mark.parametrize('controller_cmd',
                         [config.FUEL_PRIMARY_CONTROLLER_CMD],
                         ids=['primary'])
def test_shutdown_controller(os_faults_steps,
                             glance_steps,
                             controller_cmd):
    """**Scenario:** Image uploads successfully after controller shutdown.

    **Steps:**

    #. Shutdown controller node.
    #. Upload image to glance.
    """
    controller_node = os_faults_steps.get_nodes_by_cmd(controller_cmd)
    os_faults_steps.poweroff_nodes(controller_node)
    glance_steps.create_images(utils.get_file_path(config.CIRROS_QCOW2_URL))
