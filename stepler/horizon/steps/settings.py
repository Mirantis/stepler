"""
--------------
Settings steps
--------------
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

from hamcrest import assert_that, equal_to  # noqa
from urlparse import urlparse

from stepler.third_party import steps_checker

from .base import BaseSteps


class SettingsSteps(BaseSteps):
    """Settings steps."""

    def _page_settings(self):
        """Open settings page if it isn't opened."""
        return self._open(self.app.page_settings)

    @steps_checker.step
    def update_settings(self,
                        lang=None,
                        timezone=None,
                        items_per_page=None,
                        instance_log_length=None,
                        check=True):
        """Step to update user settings."""
        with self._page_settings().form_settings as form:
            if lang:
                form.combobox_lang.value = lang
            if timezone:
                form.combobox_timezone.value = timezone
            if items_per_page:
                form.field_items_per_page.value = items_per_page
            if instance_log_length:
                form.field_instance_log_length.value = instance_log_length
            form.submit()

            if check:
                self.close_notification('success')
                form.wait_for_presence()

    @steps_checker.step
    def get_current_settings(self):
        """Current user settings."""
        with self._page_settings().form_settings as form:
            current_settings = {
                'lang': form.combobox_lang.value,
                'timezone': form.combobox_timezone.value,
                'items_per_page': form.field_items_per_page.value,
                'instance_log_length': form.field_instance_log_length.value}
            return current_settings

    def _page_password(self):
        """Open page to change user password if it isn't opened."""
        return self._open(self.app.page_password)

    @steps_checker.step
    def change_user_password(self, current_password, new_password, check=True):
        """Step to change user password."""
        page_password = self._page_password()

        with page_password.form_change_password as form:
            form.field_current_password.value = current_password
            form.field_new_password.value = new_password
            form.field_confirm_password.value = new_password
            form.submit()

        if check:
            self.app.page_login.label_error_message.wait_for_presence()

    @steps_checker.step
    def check_dashboard_help_url(self, help_url):
        """Step to check dashboard help URL."""
        with self.app.page_base.dropdown_menu_account as menu:
            menu.click()
            netloc = urlparse(menu.item_help.href).netloc
            assert_that(netloc, equal_to(help_url))
            menu.click()

    @steps_checker.step
    def check_current_settings(self, expected_settings):
        """Step to check current settings."""
        assert_that(self.get_current_settings(), equal_to(expected_settings))
