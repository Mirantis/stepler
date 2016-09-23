"""
Settings steps.

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

import pom

from .base import BaseSteps


class SettingsSteps(BaseSteps):
    """Settings steps."""

    def page_settings(self):
        """Open settings page if it isn't opened."""
        return self._open(self.app.page_settings)

    @pom.timeit('Step')
    def update_settings(self,
                        lang=None,
                        timezone=None,
                        items_per_page=None,
                        instance_log_length=None,
                        check=True):
        """Step to update user settings."""
        with self.page_settings().form_settings as form:
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

    @property
    @pom.timeit('Step')
    def current_settings(self):
        """Current user settings."""
        with self.page_settings().form_settings as form:
            return {
                'lang': form.combobox_lang.value,
                'timezone': form.combobox_timezone.value,
                'items_per_page': form.field_items_per_page.value,
                'instance_log_length': form.field_instance_log_length.value}

    def page_password(self):
        """Open page to change user password if it isn't opened."""
        return self._open(self.app.page_password)

    @pom.timeit('Step')
    def change_user_password(self, current_password, new_password, check=True):
        """Step to change user password."""
        page_password = self.page_password()

        with page_password.form_change_password as form:
            form.field_current_password.value = current_password
            form.field_new_password.value = new_password
            form.field_confirm_password.value = new_password
            form.submit()

        if check:
            self.app.page_login.label_error_message.wait_for_presence()
