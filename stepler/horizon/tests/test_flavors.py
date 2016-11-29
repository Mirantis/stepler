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

    @pytest.mark.idempotent_id('ccfeddd8-a21e-4224-9608-88aa700333d5')
    def test_flavor_update_metadata(self, flavor, flavors_steps):
        """Verify that admin can update flavor metadata."""
        metadata = {next(utils.generate_ids('metadata')):
                    next(utils.generate_ids("value"))
                    for _ in range(2)}
        flavors_steps.update_metadata(flavor.name, metadata)
        flavor_metadata = flavors_steps.get_metadata(flavor.name)
        # TODO(schipiga): replace it to step.
        assert metadata == flavor_metadata

    @pytest.mark.idempotent_id('e654d077-c645-4eb7-9a7b-763a1cee3a81')
    def test_update_flavor(self, flavor, flavors_steps):
        """Verify that admin cat update flavor."""
        new_flavor_name = flavor.name + '-updated'
        with flavor.put(name=new_flavor_name):
            flavors_steps.update_flavor(flavor_name=flavor.name,
                                        new_flavor_name=new_flavor_name)

    @pytest.mark.idempotent_id('9833c67c-9aff-416f-90f7-7eeadc29993c')
    def test_modify_flavor_access(self, horizon, flavor, auth_steps,
                                  flavors_steps, instances_steps):
        """Verify that admin can modify flavor access."""
        flavors_steps.modify_access(flavor.name, project=config.ADMIN_PROJECT)

        auth_steps.logout()
        auth_steps.login(config.USER_NAME, config.USER_PASSWD)

        instances_steps.check_flavor_absent_in_instance_launch_form(flavor)

        auth_steps.logout()
        auth_steps.login(config.ADMIN_NAME, config.ADMIN_PASSWD)

    @pytest.mark.idempotent_id('2cdca1ac-c343-47f5-bb4c-ecbb319d98e7',
                               flavors_count=2)
    @pytest.mark.idempotent_id('c9ea16ff-539b-436f-8689-cbd5814abffd',
                               flavors_count=1)
    @pytest.mark.parametrize('flavors_count', [2, 1])
    def test_delete_flavors(self, flavors_count, create_flavors):
        """Verify that admin can delete flavors as batch."""
        flavor_names = list(utils.generate_ids('flavor', count=flavors_count))
        create_flavors(*flavor_names)
