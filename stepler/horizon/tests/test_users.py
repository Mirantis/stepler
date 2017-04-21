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

from stepler import config
from stepler.third_party import utils


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('b4249e0f-95eb-41cd-8d35-fccc21fdcbd1')
    def test_create_user(self, users_steps_ui):
        """**Scenario:** Verify that admin can create and delete user.

        **Steps:**

        #. Create user using UI
        #. Delete user using UI
        """
        user_name = next(utils.generate_ids('user'))
        password = next(utils.generate_ids('password'))
        users_steps_ui.create_user(user_name, password)
        users_steps_ui.delete_user(user_name)

    @pytest.mark.idempotent_id('1fc6f276-5d0b-46ca-906c-08c8e8f2752f',
                               users=1)
    @pytest.mark.idempotent_id('7aa66c15-1d7f-4d6a-96b6-740465971488',
                               users=2)
    @pytest.mark.parametrize('users', [1, 2], indirect=True)
    def test_delete_users(self, users, users_steps_ui):
        """**Scenario:** Verify that admin can delete users as bunch.

        **Setup:**

        #. Create users using API

        **Steps:**

        #. Delete users as bunch using UI
        """
        user_names = [user.name for user in users]
        users_steps_ui.delete_users(user_names)

    @pytest.mark.idempotent_id('b5116a31-404d-4391-b1d6-e35670dbadb3')
    def test_change_user_password(self, new_user_with_project, users_steps_ui,
                                  auth_steps):
        """**Scenario:** Verify that admin can change user password.

        **Setup:**

        #. Create user using API

        **Steps:**

        #. Change user password using UI
        #. Logout
        #. Login with user credentials
        #. Logout
        #. Login with admin credentials

        **Teardown:**

        #. Delete user using API
        """
        new_password = 'new-' + new_user_with_project.password

        users_steps_ui.change_user_password(new_user_with_project.username,
                                            new_password)

        auth_steps.logout()
        auth_steps.login(new_user_with_project.username, new_password)
        auth_steps.logout()
        auth_steps.login(config.ADMIN_NAME, config.ADMIN_PASSWD)

    @pytest.mark.idempotent_id('66754448-3873-4144-a15b-c5431c748566')
    def test_impossible_delete_admin_via_button(self, users_steps_ui):
        """**Scenario:** Verify that admin can't delete himself.

        **Steps:**

        #. Try to delete admin user using UI
        #. Close error notification
        #. Check that admin user is present
        """
        users_steps_ui.delete_users([config.ADMIN_NAME], check=False)
        users_steps_ui.close_notification('error')
        users_steps_ui.check_user_present(config.ADMIN_NAME)

    @pytest.mark.idempotent_id('685531db-0c6f-40e7-afc0-a65975755a14')
    def test_impossible_delete_admin_via_dropdown(self, users_steps_ui):
        """**Scenario:** Admin can't be deleted with dropdown menu.

        **Steps:**

        #. Try to delete admin user from dropdown menu using UI
        """
        users_steps_ui.check_user_not_deleted(config.ADMIN_NAME)

    @pytest.mark.idempotent_id('7c5be05a-a756-4b82-8b5c-dffb6f0d5bc1')
    def test_impossible_disable_admin(self, users_steps_ui):
        """**Scenario:** Verify that admin can't disable himself.

        **Steps:**

        #. Try to disable admin user using UI
        #. Check that user is enabled
        """
        users_steps_ui.toggle_user(config.ADMIN_NAME, enable=False,
                                   check=False)
        users_steps_ui.check_user_enable_status(config.ADMIN_NAME)

    @pytest.mark.idempotent_id('9a1c69a4-22be-43cc-8268-ae5008c2ef5b')
    def test_filter_users(self, users_steps_ui):
        """**Scenario:** Verify that admin can filter users.

        **Steps:**

        #. Filter users using UI
        """
        users_steps_ui.filter_users('admin')

    @pytest.mark.idempotent_id('beb14ed4-cd96-42f0-ba08-32a3123b7d66')
    def test_sort_users(self, users_steps_ui):
        """**Scenario:** Verify that admin can sort users.

        **Steps:**

        #. Sort users using UI
        #. Refresh page
        #. Sort users in reversed order using UI
        """
        users_steps_ui.sort_users()
        users_steps_ui.refresh_page()
        users_steps_ui.sort_users(reverse=True)

    @pytest.mark.idempotent_id('45862c62-0871-4e4f-a0ec-8cde6f970049')
    def test_disable_enable_user(self, user, users_steps_ui):
        """**Scenario:** Verify that admin can enable and disable user.

        **Setup:**

        #. Create user using API

        **Steps:**

        #. Disable user using UI
        #. Enable user using UI

        **Teardown:**

        #. Delete user using API
        """
        users_steps_ui.toggle_user(user.name, enable=False)
        users_steps_ui.toggle_user(user.name, enable=True)

    @pytest.mark.idempotent_id('4716cd34-5391-45bb-bf7c-37b5ce8c5591')
    def test_update_user(self, user, users_steps_ui):
        """**Scenario:** Verify that admin can update user.

        **Setup:**

        #. Create user using API

        **Steps:**

        #. Update user name using UI

        **Teardown:**

        #. Delete user using API
        """
        new_username = user.name + '(updated)'
        users_steps_ui.update_user(user.name, new_username)


@pytest.mark.usefixtures('user_only')
class TestUserOnly(object):
    """Tests for demo user only."""

    @pytest.mark.idempotent_id('ea9e9ac5-381d-40cc-b5e0-0393b07c6c5d')
    def test_unavailable_users_list_for_unprivileged_user(self,
                                                          users_steps_ui):
        """**Scenario:** Verify that demo user can't see users list.

        **Steps:**

        #. Check that users page is absent for demo user
        """
        users_steps_ui.check_no_users_page_in_menu()
