"""
Tests for volume backups.

@author: schipiga@mirantis.com
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

    def test_volume_backups_pagination(self, create_backups, update_settings,
                                       volumes_steps):
        """Verify that volume backups pagination works right and back."""
        backup_names = list(generate_ids('backup', count=3))
        create_backups(backup_names)
        update_settings(items_per_page=1)

        tab_backups = volumes_steps.tab_backups()

        tab_backups.table_backups.row(
            name=backup_names[2]).wait_for_presence(30)
        assert tab_backups.table_backups.link_next.is_present
        assert not tab_backups.table_backups.link_prev.is_present

        tab_backups.table_backups.link_next.click()

        tab_backups.table_backups.row(
            name=backup_names[1]).wait_for_presence(30)
        assert tab_backups.table_backups.link_next.is_present
        assert tab_backups.table_backups.link_prev.is_present

        tab_backups.table_backups.link_next.click()

        tab_backups.table_backups.row(
            name=backup_names[0]).wait_for_presence(30)
        assert not tab_backups.table_backups.link_next.is_present
        assert tab_backups.table_backups.link_prev.is_present

        tab_backups.table_backups.link_prev.click()

        tab_backups.table_backups.row(
            name=backup_names[1]).wait_for_presence(30)
        assert tab_backups.table_backups.link_next.is_present
        assert tab_backups.table_backups.link_prev.is_present

        tab_backups.table_backups.link_prev.click()

        tab_backups.table_backups.row(
            name=backup_names[2]).wait_for_presence(30)
        assert tab_backups.table_backups.link_next.is_present
        assert not tab_backups.table_backups.link_prev.is_present
