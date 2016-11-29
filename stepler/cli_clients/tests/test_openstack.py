"""
------------------------------
Tests for openstack CLI client
------------------------------
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


@pytest.mark.idempotent_id('5109e66d-4e40-42bf-a829-ee3018bae44f')
def test_server_list(server, cli_openstack_steps):
    """**Scenario:** nova list works via shell.

    **Setup:**:

    #. Create nova server and wait it active

    **Steps:**:

    #. Execute in shell ``openstack server list``

    **Teardown:**

    #. Remove nova server
    """
    cli_openstack_steps.server_list()


@pytest.mark.idempotent_id('07aa946f-46a0-40f3-9cbc-5d11f35e7fc0')
def test_baremetal_node_list(cli_openstack_steps):
    """**Scenario:** openstack baremetal list works via shell.

    **Steps:**:

    #. Execute in shell ``openstack baremetal list``
    """
    cli_openstack_steps.baremetal_node_list()
