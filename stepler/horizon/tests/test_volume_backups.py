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

from stepler.horizon.utils import generate_ids


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any user."""

    @pytest.mark.idempotent_id('7f43197f-ba2c-4962-a07a-43cbf77a779b')
    def test_volume_backups_pagination(self, create_backups, update_settings,
                                       volumes_steps_ui):
        """Verify that volume backups pagination works right and back."""
        backup_names = list(generate_ids('backup', count=3))
        create_backups(backup_names)
        update_settings(items_per_page=1)
        volumes_steps_ui.check_backups_pagination(backup_names)

    @pytest.mark.idempotent_id('dd3abd5c-0900-40a0-be3d-b284eeb6b5da')
    def test_create_volume_backup(self, create_backups):
        """**Scenario:** Create volume backup

        **Setup:**

            #. Create volume

        **Steps:**

            #. Create backup
            #. Check that backup is created

        **Teardown:**

            #. Delete backup
            #. Delete volume
        """
        backup_name = next(generate_ids('backup'))
        create_backups([backup_name])

    @pytest.mark.idempotent_id('acf12ae6-7b00-4bad-aef4-25ca3e3c3dc0')
    def test_create_volume_backup_with_long_name(self, volume,
                                                 volumes_steps_ui):
        """**Scenario:** Create volume backup with name lenght > 255

        **Setup:**

            #. Create volume

        **Steps:**

            #. Check that backup name on backup creation form can contains max
                255 symbols

        **Teardown:**

            #. Delete volume
        """
        volumes_steps_ui.check_backup_creation_form_name_field_max_lenght(
            volume.name, 255)
