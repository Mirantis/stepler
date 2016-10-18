"""
-----------
Users steps
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

import pom
from hamcrest import assert_that, equal_to  # noqa
from waiting import wait

from stepler.third_party.steps_checker import step

from .base import BaseSteps


class UsersSteps(BaseSteps):
    """Users steps."""

    def _page_users(self):
        """Open users page if it isn't opened."""
        return self._open(self.app.page_users)

    @step
    def create_user(self, username, password, project=None, role=None,
                    check=True):
        """Step to create user."""
        page_users = self._page_users()

        page_users.button_create_user.click()
        with page_users.form_create_user as form:

            form.field_name.value = username
            form.field_password.value = password
            form.field_confirm_password.value = password

            if project:
                form.combobox_project.value = project

            if role:
                form.combobox_role.value = role

            form.submit()

        if check:
            self.close_notification('success')
            page_users.table_users.row(name=username).wait_for_presence()

    @step
    def delete_user(self, username, check=True):
        """Step to delete user."""
        page_users = self._page_users()

        with page_users.table_users.row(name=username).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_users.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_users.table_users.row(name=username).wait_for_absence()

    @step
    def delete_users(self, usernames, check=True):
        """Step to delete users."""
        page_users = self._page_users()

        for username in usernames:
            page_users.table_users.row(name=username).checkbox.select()

        page_users.button_delete_users.click()
        page_users.form_confirm.submit()

        if check:
            self.close_notification('success')

            for username in usernames:
                page_users.table_users.row(name=username).wait_for_absence()

    @step
    def change_user_password(self, username, new_password, check=True):
        """Step to change user password."""
        page_users = self._page_users()

        with page_users.table_users.row(name=username).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_change_password.click()

        with page_users.form_change_password as form:
            form.field_password.value = new_password
            form.field_confirm_password.value = new_password
            form.submit()

            if check:
                self.close_notification('success')
                form.wait_for_absence()

    @step
    def filter_users(self, query, check=True):
        """Step to filter users."""
        page_users = self._page_users()

        page_users.field_filter_users.value = query
        page_users.button_filter_users.click()
        pom.sleep(1, 'Wait table will be refreshed')

        if check:

            def check_rows():
                for row in page_users.table_users.rows:
                    if not (row.is_present and
                            query in row.link_username.value):
                        return False
                return True

            wait(check_rows, timeout_seconds=10, sleep_seconds=0.1)

    @step
    def sort_users(self, reverse=False, check=True):
        """Step to sort users."""
        with self._page_users().table_users as table:

            table.header.cell('name').click()
            if reverse:
                table.header.cell('name').click()
            pom.sleep(1, 'Wait table will be refreshed')

            if check:

                def check_sort():
                    usernames = [row.link_username.value for row in table.rows]
                    expected_usernames = sorted(usernames)

                    if reverse:
                        expected_usernames = list(reversed(expected_usernames))

                    return usernames == expected_usernames

                wait(check_sort, timeout_seconds=10, sleep_seconds=0.1)

    @step
    def toggle_user(self, username, enable, check=True):
        """Step to disable user."""
        if enable:
            curr_status = 'No'
            need_status = 'Yes'
        else:
            curr_status = 'Yes'
            need_status = 'No'

        with self._page_users().table_users.row(name=username) as row:
            assert row.cell('enabled').value == curr_status

            with row.dropdown_menu as menu:
                menu.button_toggle.click()
                menu.item_toggle_user.click()

            if check:
                self.close_notification('success')
                assert_that(row.cell('enabled').value, equal_to(need_status))

    @step
    def update_user(self, username, new_username, check=True):
        """Step to update user."""
        page_users = self._page_users()

        with page_users.table_users.row(name=username).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_default.click()

        with page_users.form_update_user as form:
            form.field_name.value = new_username
            form.submit()

        if check:
            self.close_notification('success')
            page_users.table_users.row(name=new_username).wait_for_presence()

    @step
    def check_user_present(self, user_name):
        """Step to check user is present."""
        with self._page_users().table_users.row(name=user_name) as row:
            assert_that(row.is_present, equal_to(True))

    @step
    def check_user_not_deleted(self, user_name):
        """Step to check user is not deleted."""
        with self._page_users().table_users.row(
                name=user_name).dropdown_menu as menu:
            menu.button_toggle.click()
            assert_that(menu.item_delete.is_present, equal_to(False))

    @step
    def check_user_enable_status(self, user_name, is_enabled=True):
        """Step to check user enable status."""
        enable_value = 'Yes' if is_enabled else 'No'
        with self._page_users().table_users.row(
                name=user_name).cell('enabled') as cell:
            assert_that(cell.value, equal_to(enable_value))

    @step
    def check_empty_users_list(self):
        """Step to check users list is empty."""
        page_users = self._page_users()
        self.close_notification('info')
        assert_that(page_users.table_users.rows, equal_to(False))
