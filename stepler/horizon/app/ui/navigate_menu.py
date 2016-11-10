"""
-------------
Navigate menu
-------------
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
from waiting import wait


class NavigateMenu(ui.Block):
    """Navigate menu."""

    _item_selector = './li/a[contains(., "{}")]'
    _sub_menu_selector = ('./li/ul[contains(@class, "collapse") and '
                          'preceding-sibling::a[contains(., "{}")]]')

    @pom.timeit
    def go_to(self, item_names):
        """Go to page via navigate menu.

        Arguments:
            - item_names: list of items of navigate menu.
        """
        container = self
        last_name = item_names[-1]

        for item_name in item_names:
            item = ui.UI(By.XPATH, self._item_selector.format(item_name))
            item.container = container

            if item_name == last_name:
                item.click()
                break

            sub_menu = ui.Block(By.XPATH,
                                self._sub_menu_selector.format(item_name))
            sub_menu.container = container

            if not _is_expanded(sub_menu):
                item.click()
                wait(lambda: _is_expanded(sub_menu),
                     timeout_seconds=10, sleep_seconds=0.1)

            container = sub_menu

    def has_item(self, item_names):
        """Check that navigate menu has item.

        Args:
            item_names (list): list of items of navigate menu.

        Returns:
            bool: is items in menu
        """
        container = self
        last_name = item_names[-1]

        for item_name in item_names:
            item = ui.UI(By.XPATH, self._item_selector.format(item_name))
            item.container = container

            if not item.is_present:
                return False

            if item_name == last_name:
                break

            sub_menu = ui.Block(By.XPATH,
                                self._sub_menu_selector.format(item_name))
            sub_menu.container = container

            if not sub_menu.is_present:
                return False

            if not _is_expanded(sub_menu):
                item.click()
                wait(lambda: _is_expanded(sub_menu),
                     timeout_seconds=10, sleep_seconds=0.1)

            container = sub_menu

        return True


def _is_expanded(menu):
    return menu.is_present and 'in' in menu.get_attribute('class').split()
