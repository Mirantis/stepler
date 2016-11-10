"""
-----------
Users tests
-----------
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
    @pytest.mark.idempotent_id('1fc6f276-5d0b-46ca-906c-08c8e8f2752f')
    def test_delete_users(self, users_count, create_users):
        """Verify that admin can create users and delete them as batch."""
        user_names = list(generate_ids('user', count=users_count))
        create_users(user_names)

    @pytest.mark.idempotent_id('b5116a31-404d-4391-b1d6-e35670dbadb3')
    def test_change_user_password(self, user, users_steps, auth_steps):
        """Verify that admin can change user password."""
        new_password = 'new-' + user.password
        with user.put(password=new_password):
            users_steps.change_user_password(user.name, new_password)

        auth_steps.logout()
        auth_steps.login(user.name, user.password)
        auth_steps.logout()
        auth_steps.login(config.ADMIN_NAME, config.ADMIN_PASSWD)

    @pytest.mark.idempotent_id('66754448-3873-4144-a15b-c5431c748566')
    def test_impossible_delete_admin_via_button(self, users_steps):
        """Verify that admin can't delete himself."""
        users_steps.delete_users([config.ADMIN_NAME], check=False)
        users_steps.close_notification('error')
        users_steps.check_user_present(config.ADMIN_NAME)

    @pytest.mark.idempotent_id('685531db-0c6f-40e7-afc0-a65975755a14')
    def test_impossible_delete_admin_via_dropdown(self, users_steps):
        """Verify that admin can't delete himself with dropdown menu."""
        users_steps.check_user_not_deleted(config.ADMIN_NAME)

    @pytest.mark.idempotent_id('7c5be05a-a756-4b82-8b5c-dffb6f0d5bc1')
    def test_impossible_disable_admin(self, horizon, users_steps):
        """Verify that admin can't disable himself."""
        users_steps.toggle_user(config.ADMIN_NAME, enable=False, check=False)
        users_steps.check_user_enable_status(config.ADMIN_NAME)

    @pytest.mark.idempotent_id('9a1c69a4-22be-43cc-8268-ae5008c2ef5b')
    def test_filter_users(self, users_steps):
        """Verify that admin can filter users."""
        users_steps.filter_users('admi')

    @pytest.mark.idempotent_id('beb14ed4-cd96-42f0-ba08-32a3123b7d66')
    def test_sort_users(self, users_steps):
        """Verify that admin can sort users."""
        users_steps.sort_users()
        users_steps.refresh_page()
        users_steps.sort_users(reverse=True)

    @pytest.mark.idempotent_id('45862c62-0871-4e4f-a0ec-8cde6f970049')
    def test_disable_enable_user(self, user, users_steps):
        """Verify that admin can enable and disable user."""
        users_steps.toggle_user(user.name, enable=False)
        users_steps.toggle_user(user.name, enable=True)

    @pytest.mark.idempotent_id('4716cd34-5391-45bb-bf7c-37b5ce8c5591')
    def test_update_user(self, user, users_steps):
        """Verify that admin can update user."""
        new_username = user.name + '(updated)'
        with user.put(name=new_username):
            users_steps.update_user(user.name, new_username)


@pytest.mark.usefixtures('user_only')
class TestUserOnly(object):
    """Tests for demo user only."""

    @pytest.mark.idempotent_id('ea9e9ac5-381d-40cc-b5e0-0393b07c6c5d')
    def test_unavailable_users_list_for_unprivileged_user(self, users_steps):
        """Verify that demo user can't see users list."""
        users_steps.check_no_users_page_in_menu()
