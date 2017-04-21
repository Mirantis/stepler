"""
-------------------
User settings tests
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


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('dabd9a5c-87de-462f-9f8c-e387d8ba39b7')
    def test_dashboard_help_url(self, new_user_login, settings_steps_ui):
        """**Scenario:** Verify that user can open dashboard help url.

        **Setup:**

        #. Create user using API
        #. Login as new user

        **Steps:**

        #. Check dashboard help url using UI

        **Teardown:**

        #. Delete user using API
        """
        settings_steps_ui.check_dashboard_help_url("docs.openstack.org")

    @pytest.mark.idempotent_id('94194097-802b-485c-9c5a-143d30e95dd6')
    def test_change_own_password(self,
                                 new_user_login,
                                 auth_steps,
                                 settings_steps_ui):
        """**Scenario:** Verify that user can change it's password.

        **Setup:**

        #. Create user using API
        #. Login as new user

        **Steps:**

        #. Change user password using UI
        #. Try to login using old password
        #. Check that alert is present
        #. Login using new password

        **Teardown:**

        #. Delete user using API
        """
        new_password = 'new-' + new_user_login.password

        settings_steps_ui.change_user_password(new_user_login.password,
                                               new_password)
        auth_steps.login(new_user_login.username,
                         new_user_login.password,
                         check=False)
        auth_steps.check_alert_present()

        auth_steps.login(new_user_login.username,
                         new_password)

    @pytest.mark.idempotent_id('870a69ed-b413-4b44-9a2b-1c1e774ad841')
    def test_change_own_settings(self, new_user_login, update_settings,
                                 settings_steps_ui):
        """**Scenario:** Verify that user can change his settings.

        **Setup:**

        #. Create user using API
        #. Login as new user

        **Steps:**

        #. Update user settings using UI
        #. Refresh page
        #. Check that settings have been updated using UI

        **Teardown:**

        #. Restore initial values for settings
        #. Delete user using API
        """
        settings = {
            'lang': 'British English (en-gb)',
            'timezone': 'UTC -05:00: Jamaica Time',
            'items_per_page': '1',
            'instance_log_length': '1'}

        update_settings(**settings)
        settings_steps_ui.refresh_page()

        settings_steps_ui.check_current_settings(expected_settings=settings)
