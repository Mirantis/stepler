"""
-----------------------------
Neutron conntrack zones tests
-----------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from stepler import config


@pytest.mark.idempotent_id('3e21c239-c95a-49ea-b518-9b38ca7ad3ea')
def test_ssh_unavailable_after_detach_floating_ip(
        nova_floating_ip,
        server,
        server_steps):
    """**Scenario:** Check ssh by floating ip for server after deleting ip.

    **Setup:**

    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Open ssh connection to server, check that it operable
    #. Detach floating IP address from server
    #. Check that opened SSH connection is not operable
    #. Check that new SSH connection can't be established

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    """
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_ssh = server_steps.get_server_ssh(server)
    with server_ssh:
        server_steps.check_active_ssh_connection(server_ssh)
        server_steps.detach_floating_ip(server, nova_floating_ip)
        server_steps.check_active_ssh_connection(
            server_ssh,
            must_operable=False,
            timeout=config.FLOATING_IP_DETACH_TIMEOUT)
    server_steps.check_ssh_connection_establishment(
        server_ssh, must_work=False)
