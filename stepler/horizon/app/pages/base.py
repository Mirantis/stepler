"""
-------------------------
Base page of user account
-------------------------
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
from pom import ui
from selenium.webdriver.common.by import By

from stepler.horizon.app import ui as _ui


@ui.register_ui(button_close=ui.Button(By.CSS_SELECTOR, 'a.close'))
class Notification(ui.Block):
    """Notification popup window."""

    levels = {'error': 'alert-danger',
              'info': 'alert-info',
              'success': 'alert-success'}


class FormConfirmDelete(_ui.Form):
    """Form to confirm deletions."""

    submit_locator = By.CSS_SELECTOR, '.btn.btn-danger'


@ui.register_ui(
    form_confirm_delete=FormConfirmDelete(
        By.CSS_SELECTOR, 'div.modal-content'),
    navigate_menu=_ui.NavigateMenu(By.ID, 'sidebar-accordion'))
class PageBase(pom.Page, _ui.InitiatedUI):
    """Base page of user account."""

    url = '/'
    navigate_items = None

    def notification(self, level):
        """Get notification by level.

        Arguments:
            - level: string, level of notification: "success", "info", "error".
        """
        selector = 'div.alert.{}'.format(Notification.levels[level])
        _notification = Notification(By.CSS_SELECTOR, selector)
        _notification.container = self
        return _notification

    def navigate(self, navigate_items):
        """Open page via navigation menu."""
        self.navigate_menu.go_to(navigate_items)
