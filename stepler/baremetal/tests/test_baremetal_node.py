"""
---------------------------
Ironic baremetal node tests
---------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest
from stepler import config


@pytest.mark.idempotent_id('fce98286-30c1-420d-8d35-7660907ec1ff')
def test_create_server_on_baremetal_node(keypair,
                                         baremetal_flavor,
                                         baremetal_ubuntu_image,
                                         baremetal_network,
                                         nova_floating_ip,
                                         server_steps):
    """**Scenario:** Launch server on baremetal node.

    **Setup:**

    #. Create keypair
    #. Create baremetal flavor
    #. Upload baremetal ubuntu image
    #. Create floating ip

    **Steps:**

    #. Create and boot server
    #. Check that server status is active
    #. Attach floating ip to server
    #. Check ssh access to server

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
                                         username=config.UBUNTU_USERNAME)[0]
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.get_server_ssh(server)
