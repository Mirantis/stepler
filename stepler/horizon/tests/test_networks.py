"""
-------------
Network tests
-------------
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


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any user."""

    @pytest.mark.idempotent_id('6e212b0c-503e-4339-a504-4548344291ee',
                               any_one='admin')
    @pytest.mark.idempotent_id('6467bf60-2ee3-4abd-9f00-7471f7985a32',
                               any_one='user')
    def test_subnet_add(self, network, networks_steps_ui):
        """**Scenario:** Verify that user can add subnet.

        **Setup:**

        #. Create network using API

        **Steps:**

        #. Add subnet to network using UI

        **Teardown:**

        #. Delete subnet using API
        #. Delete network using API
        """
        networks_steps_ui.add_subnet(network['name'])

    @pytest.mark.idempotent_id('1461428b-fa96-49b4-b8b2-71e504739821',
                               any_one='admin')
    @pytest.mark.idempotent_id('cd40f3b7-81d2-47e1-9737-925ce0d9bf6d',
                               any_one='user')
    def test_network_topology_page_exists(self, networks_steps_ui):
        """**Scenario:** Verify that page Network Topology exists.

        **Steps:**

        #. Open Network Topology page
        """
        networks_steps_ui.network_topology_page_availability()


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('ce3c02b9-ecb3-48c9-9ef4-b48172c6c111')
    def test_create_shared_network(self, networks_steps_ui):
        """**Scenario:** Verify that admin can create shared network.

        **Steps:**

        #. Create shared network using UI
        #. Try to delete network from network tab using UI
        #. Close error notification
        #. Check that network is still present
        #. Delete network from admin network tab using UI
        """
        network_name = networks_steps_ui.create_network(shared=True)
        networks_steps_ui.delete_networks([network_name], check=False)
        networks_steps_ui.close_notification('error')
        networks_steps_ui.check_network_present(network_name)
        networks_steps_ui.admin_delete_network(network_name)


@pytest.mark.usefixtures('user_only')
class TestUserOnly(object):
    """Tests for demo only."""

    @pytest.mark.idempotent_id('81869139-da99-4595-9bee-55862112ae1b')
    def test_not_create_shared_network(self, networks_steps_ui):
        """**Scenario:** Verify that user can not create shared network.

        **Steps:**

        #. Check that user can't make network shared
        """
        networks_steps_ui.user_try_to_create_shared_network()
