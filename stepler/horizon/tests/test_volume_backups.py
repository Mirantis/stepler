"""
-------------------
Volume backup tests
-------------------
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

from stepler.third_party import utils

pytestmark = pytest.mark.requires('horizon_cinder_backup')


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any user."""

    @pytest.mark.idempotent_id('7f43197f-ba2c-4962-a07a-43cbf77a779b',
                               any_one='admin')
    @pytest.mark.idempotent_id('f49eef31-b26a-496c-8f0f-2465a97d04cf',
                               any_one='user')
    @pytest.mark.parametrize('volume_backups', [3], ids=[''], indirect=True)
    def test_volume_backups_pagination(self, backup_steps, volume_backups,
                                       update_settings, volumes_steps_ui):
        """**Scenario:** Verify that volume backups pagination works.

        **Setup:**

        #. Create volume using API
        #. Create some backups using API

        **Steps:**

        #. Update ``items_per_page`` parameter to 1 using UI
        #. Check backups pagination using UI

        **Teardown:**

        #. Delete backups using API
        #. Delete volumes using API
        """
        backup_names = [backup.name or backup.id
                        for backup in backup_steps.get_backups()]
        update_settings(items_per_page=1)
        volumes_steps_ui.check_backups_pagination(backup_names)

    @pytest.mark.idempotent_id('dd3abd5c-0900-40a0-be3d-b284eeb6b5da',
                               any_one='admin')
    @pytest.mark.idempotent_id('9cc2b22d-6234-4fb3-aad8-abe7d39cc870',
                               any_one='user')
    def test_create_volume_backup(self, volume, volumes_steps_ui):
        """**Scenario:** Create volume backup.

        **Setup:**

        #. Create volume using API

        **Steps:**

        #. Create backup using UI

        **Teardown:**

        #. Delete backup using API
        #. Delete volume using API
        """
        volumes_steps_ui.create_backup(volume.name)

    @pytest.mark.idempotent_id('95a60e66-8e12-48ea-a7b2-c9b49ca35e45',
                               any_one='admin')
    @pytest.mark.idempotent_id('7ab4eb5a-e00a-427e-9128-fff277a38e85',
                               any_one='user')
    @pytest.mark.parametrize('volume_backups', [3], ids=[''], indirect=True)
    def test_delete_volume_backups(self, volume_backups, volumes_steps_ui):
        """**Scenario:** Delete volume backups as bunch.

        **Setup:**

        #. Create volume using API
        #. Create backups using API

        **Steps:**

        #. Delete backups as bunch using UI

        **Teardown:**

        #. Delete volume using API
        """
        backup_names = [backup.name or backup.id for backup in volume_backups]
        volumes_steps_ui.delete_backups(backup_names)

    @pytest.mark.idempotent_id('acf12ae6-7b00-4bad-aef4-25ca3e3c3dc0',
                               any_one='admin')
    @pytest.mark.idempotent_id('bcdb65f1-49a5-4623-9bca-dd08d31a30bb',
                               any_one='user')
    def test_volume_backup_form_max_name_length(self, volume,
                                                volumes_steps_ui):
        """**Scenario:** Create volume backup with name length > 255.

        **Setup:**

        #. Create volume using API

        **Steps:**

        #. Open backup creation form using UI
        #. Check that backup name input can't contains more than 255 symbols

        **Teardown:**

        #. Delete volume using API
        """
        volumes_steps_ui.check_backup_creation_form_name_field_max_length(
            volume.name, 255)

    @pytest.mark.idempotent_id('42020f62-06d5-49f5-8b78-08d40b518b17',
                               any_one='admin')
    @pytest.mark.idempotent_id('6018b01d-0b3b-41fb-a7ca-46b78c2cc7a3',
                               any_one='user')
    def test_create_volume_backup_with_description(self, volume,
                                                   volumes_steps_ui):
        """**Scenario:** Create volume backup with description.

        **Setup:**

        #. Create volume using API

        **Steps:**

        #. Create backup with description

        **Teardown:**

        #. Delete backup using API
        #. Delete volume using API
        """
        backup_description = next(utils.generate_ids('backup', length=30))
        volumes_steps_ui.create_backup(volume.name,
                                       description=backup_description)

    @pytest.mark.idempotent_id('36a02ea4-ce4d-4f45-b461-954ded1ea171',
                               any_one='admin')
    @pytest.mark.idempotent_id('abb97b8e-6539-413a-b3b0-7e770eeb83e2',
                               any_one='user')
    def test_create_volume_backup_with_max_length_description(
            self, volume, volumes_steps_ui):
        """**Scenario:** Create volume backup with description length == max.

        **Setup:**

        #. Create volume using API

        **Steps:**

        #. Create backup with long (255 symbols) description using UI

        **Teardown:**

        #. Delete backup using API
        #. Delete volume using API
        """
        backup_description = next(utils.generate_ids('backup', length=255))
        volumes_steps_ui.create_backup(volume.name,
                                       description=backup_description)
