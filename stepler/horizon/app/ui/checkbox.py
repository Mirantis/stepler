"""
Themable checkbox.

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
from pom.ui.base import WebElementProxy
from selenium.webdriver.common.by import By


class CheckBox(pom.ui.CheckBox):
    """Themable checkbox."""

    @property
    @pom.ui.wait_for_presence
    def is_selected(self):
        """Define is checkbox selected."""
        return self._webelement.is_selected()

    @property
    @pom.cache
    def webelement(self):
        """Label of checkbox."""
        web_id = self._webelement.get_attribute('id')
        label_locator = By.CSS_SELECTOR, 'label[for="{}"]'.format(web_id)

        return WebElementProxy(
            lambda: self.container.find_element(label_locator),
            ui_info=repr(self))

    @property
    def _webelement(self):
        return super(CheckBox, self).webelement
