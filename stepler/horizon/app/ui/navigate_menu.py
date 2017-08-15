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

    _item_selector = './/a[contains(., "{}")]'
    _sub_container_selector = './parent::*'

    @pom.timeit
    def go_to(self, item_names):
        """Go to page via navigate menu.

        Arguments:
            - item_names: list of items of navigate menu.
        """
        container = self

        parent_item = None

        for item_name in item_names:
            item = ui.Block(By.XPATH, self._item_selector.format(item_name))
            item.container = container

            if not item.webelement.is_displayed() and parent_item:
                parent_item.click()
                wait(item.webelement.is_displayed,
                     timeout_seconds=10, sleep_seconds=0.1)

            container = ui.Block(By.XPATH, self._sub_container_selector)
            container.container = item
            parent_item = item

        item.click()

    def has_item(self, item_names):
        """Check that navigate menu has item.

        Args:
            item_names (list): list of items of navigate menu.

        Returns:
            bool: is items in menu
        """
        container = self

        parent_item = None

        for item_name in item_names:
            item = ui.Block(By.XPATH, self._item_selector.format(item_name))
            item.container = container

            try:
                item.webelement.tag_name
            except Exception:
                return False

            if not item.webelement.is_displayed() and parent_item:
                parent_item.click()
                wait(item.webelement.is_displayed,
                     timeout_seconds=10, sleep_seconds=0.1)

            container = ui.Block(By.XPATH, self._sub_container_selector)
            container.container = item
            parent_item = item

        return True
