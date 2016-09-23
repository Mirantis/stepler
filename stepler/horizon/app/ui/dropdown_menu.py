"""
Dropdown menu component.

Usually used in tables to add actions for rows.

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

from pom import ui
from selenium.webdriver.common.by import By


@ui.register_ui(
    button_toggle=ui.Button(By.CSS_SELECTOR, '.dropdown-toggle'),
    item_default=ui.UI(By.CSS_SELECTOR, 'a:nth-of-type(1)'),
    item_delete=ui.UI(By.CSS_SELECTOR, '[id$="action_delete"]'),
    item_edit=ui.UI(By.CSS_SELECTOR, '[id$="action_edit"]'))
class DropdownMenu(ui.Block):
    """Dropdown menu."""

    def __init__(self, *args, **kwgs):
        """Constructor.

        It has predefined selector.
        """
        super(DropdownMenu, self).__init__(*args, **kwgs)
        self.locator = By.CSS_SELECTOR, '.btn-group'
