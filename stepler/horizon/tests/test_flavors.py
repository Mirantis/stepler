"""
------------
Flavor tests
------------
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
from stepler.third_party import utils


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('4b913841-1952-47ff-a904-a256a268b182')
    def test_create_delete_flavor(self, flavors_steps_ui):
        """**Scenario:** Verify that admin can create and delete flavor.

        **Steps:**

        #. Create flavor using UI
        #. Delete flavor using UI
        """
        flavor_name = flavors_steps_ui.create_flavor()
        flavors_steps_ui.delete_flavor(flavor_name)

    @pytest.mark.idempotent_id('ccfeddd8-a21e-4224-9608-88aa700333d5')
    def test_flavor_update_metadata(self, flavor, flavors_steps_ui):
        """**Scenario:** Verify that admin can update flavor metadata.

        **Setup:**

        #. Create flavor using API

        **Steps:**

        #. Update flavor metadata using UI

        **Teardown:**

        #. Delete flavor using API
        """
        metadata = {next(utils.generate_ids('metadata')):
                    next(utils.generate_ids("value"))
                    for _ in range(2)}
        flavors_steps_ui.update_metadata(flavor.name, metadata)

    @pytest.mark.idempotent_id('e654d077-c645-4eb7-9a7b-763a1cee3a81')
    def test_update_flavor(self, flavor, flavors_steps_ui):
        """**Scenario:** Verify that admin cat update flavor.

        **Setup:**

        #. Create flavor using API

        **Steps:**

        #. Update flavor name using UI

        **Teardown:**

        #. Delete flavor using API
        """
        new_flavor_name = flavor.name + '-updated'
        flavors_steps_ui.update_flavor(flavor_name=flavor.name,
                                       new_flavor_name=new_flavor_name)

    @pytest.mark.idempotent_id('9833c67c-9aff-416f-90f7-7eeadc29993c')
    def test_modify_flavor_access(self, flavor, auth_steps, flavors_steps_ui,
                                  instances_steps_ui):
        """**Scenario:** Verify that admin can modify flavor access.

        **Setup:**

        #. Create flavor using API

        **Steps:**

        #. Change flavor access using UI
        #. Logout
        #. Login with user credentials
        #. Check flavor is absent in instance launch form
        #. Logout
        #. Login with admin credentials

        **Teardown:**

        #. Delete flavor using API
        """
        flavors_steps_ui.modify_access(flavor.name,
                                       project=config.ADMIN_PROJECT)

        auth_steps.logout()
        auth_steps.login(config.USER_NAME, config.USER_PASSWD)

        instances_steps_ui.check_flavor_absent_in_instance_launch_form(flavor)

        auth_steps.logout()
        auth_steps.login(config.ADMIN_NAME, config.ADMIN_PASSWD)

    @pytest.mark.idempotent_id('2cdca1ac-c343-47f5-bb4c-ecbb319d98e7',
                               flavors=2)
    @pytest.mark.idempotent_id('c9ea16ff-539b-436f-8689-cbd5814abffd',
                               flavors=1)
    @pytest.mark.parametrize('flavors', [1, 2], indirect=True)
    def test_delete_flavors(self, flavors, flavors_steps_ui):
        """**Scenario:** Verify that admin can delete flavors as bunch.

        **Setup:**

        #. Create flavors using API

        **Steps:**

        #. Delete flavors as bunch using UI
        """
        flavor_names = [flavor.name for flavor in flavors]
        flavors_steps_ui.delete_flavors(flavor_names)
