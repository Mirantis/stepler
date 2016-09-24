"""
-------------------
User settings tests
-------------------

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

from urlparse import urlparse

import pytest

from stepler.horizon.config import ADMIN_NAME, ADMIN_PASSWD


@pytest.yield_fixture
def new_user_account(user, auth_steps):
    """Fixture to log in new user account."""
    auth_steps.logout()
    auth_steps.login(user.name, user.password)

    yield

    auth_steps.logout()
    auth_steps.login(ADMIN_NAME, ADMIN_PASSWD)


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    def test_dashboard_help_url(self, new_user_account, horizon):
        """Verify that user can open dashboard help url."""
        with horizon.page_base.dropdown_menu_account as menu:
            menu.click()
            assert urlparse(menu.item_help.href).netloc == "docs.openstack.org"
            menu.click()

    def test_change_own_password(self, horizon, user, new_user_account,
                                 auth_steps, settings_steps):
        """Verify that user can change it's password."""
        new_password = 'new-' + user.password
        with user.put(password=new_password):
            settings_steps.change_user_password(user.password, new_password)

            auth_steps.login(user.name, user.password, check=False)
            horizon.page_login.label_alert_message.wait_for_presence()

        auth_steps.login(user.name, user.password)

    def test_change_own_settings(self, horizon, new_user_account,
                                 update_settings, settings_steps):
        """Verify that user can change his settings."""
        new_settings = {
            'lang': 'British English (en-gb)',
            'timezone': 'UTC -05:00: Jamaica Time',
            'items_per_page': '1',
            'instance_log_length': '1'}

        update_settings(**new_settings)
        horizon.page_settings.refresh()

        assert settings_steps.current_settings == new_settings
