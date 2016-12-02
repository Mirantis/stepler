"""
---------------------
Ironic services tests
---------------------
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


@pytest.mark.idempotent_id('a0b0d6f7-0952-4e29-9148-a4ada8cf349c')
def test_ironic_api_service(keypair,
                            baremetal_flavor,
                            baremetal_network,
                            baremetal_ubuntu_image,
                            nova_floating_ip,
                            ironic_api_node,
                            server_steps,
                            os_faults_steps):
    """**Scenario:** Launch server with stopped service ironic-api
    on one of node.

    **Setup:**

    #. Create keypair
    #. Create baremetal flavor
    #. Upload baremetal ubuntu image
    #. Create floating ip
    #. Get node with service ironic-api

    **Steps:**

    #. Create and boot server
    #. Stop service ironic-api
    #. Check that server status is active
    #. Attach floating ip to server
    #. Check ssh access to server
    #. Start service ironic-api

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    #. Delete image
    #. Delete flavor
    #. Delete keypair
    """
    server = server_steps.create_servers(image=baremetal_ubuntu_image,
                                         flavor=baremetal_flavor,
                                         networks=[baremetal_network],
                                         keypair=keypair,
                                         username=config.UBUNTU_USERNAME,
                                         check=False)[0]
    os_faults_steps.terminate_service(config.IRONIC_API, nodes=ironic_api_node)

    server_steps.check_server_status(server,
                                     expected_statuses=[config.STATUS_ACTIVE],
                                     transit_statuses=[config.STATUS_BUILD],
                                     timeout=config.SERVER_ACTIVE_TIMEOUT)

    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.get_server_ssh(server)
    os_faults_steps.start_service(config.IRONIC_API, nodes=ironic_api_node)
