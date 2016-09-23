"""
Horizon steps for authentication.

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


class AuthSteps(BaseSteps):
    """Authentication steps."""

    def page_login(self):
        """Open login page if it's not opened."""
        return self._open(self.app.page_login)

    @pom.timeit('Step')
    def login(self, username, password, check=True):
        """Step to log in user account.

        Arguments:
            - username: string, user name.
            - password: string, user password.
        """
        with self.page_login().form_login as form:
            form.field_username.value = username
            form.field_password.value = password
            form.submit()

        if check:
            self.app.page_base.dropdown_menu_account.wait_for_presence(30)

        self.app.current_username = username

    @pom.timeit('Step')
    def logout(self, check=True):
        """Step to log out user account."""
        with self.app.page_base.dropdown_menu_account as menu:
            menu.click()
            menu.item_exit.click()

        if check:
            self.app.page_login.form_login.wait_for_presence(30)

        self.app.current_username = None
        self.app.current_project = None
