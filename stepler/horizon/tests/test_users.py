"""
-----------
Users tests
-----------

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

from stepler.horizon import config
from stepler.horizon.utils import generate_ids


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.parametrize('users_count', [1, 2])
    def test_delete_users(self, users_count, create_users):
        """Verify that admin can create users and delete them as batch."""
        user_names = list(generate_ids('user', count=users_count))
        create_users(user_names)

    def test_change_user_password(self, user, users_steps, auth_steps):
        """Verify that admin can change user password."""
        new_password = 'new-' + user.password
        with user.put(password=new_password):
            users_steps.change_user_password(user.name, new_password)

        auth_steps.logout()
        auth_steps.login(user.name, user.password)
        auth_steps.logout()
        auth_steps.login(config.ADMIN_NAME, config.ADMIN_PASSWD)

    def test_impossible_delete_admin_via_button(self, users_steps):
        """Verify that admin can't delete himself."""
        users_steps.delete_users([config.ADMIN_NAME], check=False)
        users_steps.close_notification('error')
        # TODO(schipiga): move it to check step
        # assert users_steps.page_users().table_users.row(
        #     name=config.ADMIN_NAME).is_present

    def test_impossible_delete_admin_via_dropdown(self, users_steps):
        """Verify that admin can't delete himself with dropdown menu."""
        # TODO(schipiga): move it to check step
        # with users_steps.page_users().table_users.row(
        #         name=config.ADMIN_NAME).dropdown_menu as menu:

        #     menu.button_toggle.click()
        #     assert not menu.item_delete.is_present

    def test_impossible_disable_admin(self, horizon, users_steps):
        """Verify that admin can't disable himself."""
        users_steps.toggle_user(config.ADMIN_NAME, enable=False, check=False)
        # TODO(schipiga): move it to check step
        # horizon.page_users.refresh()
        # horizon.page_users.table_users.row(
        #     name=config.ADMIN_NAME).cell('enabled').value == 'Yes'

    def test_filter_users(self, users_steps):
        """Verify that admin can filter users."""
        users_steps.filter_users('admi')

    def test_sort_users(self, users_steps):
        """Verify that admin can sort users."""
        users_steps.sort_users()
        # TODO(schipiga): move it to check step
        # users_steps.page_users().refresh()
        users_steps.sort_users(reverse=True)

    def test_disable_enable_user(self, user, users_steps):
        """Verify that admin can enable and disable user."""
        users_steps.toggle_user(user.name, enable=False)
        users_steps.toggle_user(user.name, enable=True)

    def test_update_user(self, user, users_steps):
        """Verify that admin can update user."""
        new_username = user.name + '(updated)'
        with user.put(name=new_username):
            users_steps.update_user(user.name, new_username)


@pytest.mark.usefixtures('user_only')
class TestUserOnly(object):
    """Tests for demo user only."""

    def test_unavailable_users_list_for_unprivileged_user(
            self, horizon, users_steps):
        """Verify that demo user can't see users list."""
        # TODO(schipiga): move it to check step
        # horizon.page_users.open()
        # users_steps.close_notification('info')
        # assert not horizon.page_users.table_users.rows
