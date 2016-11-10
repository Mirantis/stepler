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
from hamcrest import assert_that, equal_to  # noqa

from stepler.horizon import config


@pytest.yield_fixture
def new_user_account(user, auth_steps):
    """Fixture to log in new user account."""
    auth_steps.logout()
    auth_steps.login(user.name, user.password)

    yield

    auth_steps.logout()
    auth_steps.login(config.ADMIN_NAME, config.ADMIN_PASSWD)


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('dabd9a5c-87de-462f-9f8c-e387d8ba39b7')
    def test_dashboard_help_url(self, new_user_account, settings_steps):
        """Verify that user can open dashboard help url."""
        settings_steps.check_dashboard_help_url("docs.openstack.org")

    @pytest.mark.idempotent_id('94194097-802b-485c-9c5a-143d30e95dd6')
    def test_change_own_password(self, user, new_user_account, auth_steps,
                                 settings_steps):
        """Verify that user can change it's password."""
        new_password = 'new-' + user.password
        with user.put(password=new_password):
            settings_steps.change_user_password(user.password, new_password)

            auth_steps.login(user.name, user.password, check=False)
            auth_steps.check_alert_present()

        auth_steps.login(user.name, user.password)

    @pytest.mark.idempotent_id('870a69ed-b413-4b44-9a2b-1c1e774ad841')
    def test_change_own_settings(self, new_user_account, update_settings,
                                 settings_steps):
        """Verify that user can change his settings."""
        new_settings = {
            'lang': 'British English (en-gb)',
            'timezone': 'UTC -05:00: Jamaica Time',
            'items_per_page': '1',
            'instance_log_length': '1'}

        update_settings(**new_settings)
        settings_steps.refresh_page()

        assert_that(settings_steps.get_current_settings(),
                    equal_to(new_settings))
