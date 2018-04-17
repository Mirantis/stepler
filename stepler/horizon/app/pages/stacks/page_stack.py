"""
---------
Stack page
----------
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

from ..base import PageBase


@ui.register_ui()
class Info(ui.Block):
    """Stack info table."""

    _property_name_locator = By.TAG_NAME, 'dt'
    _property_value_locator = By.XPATH, 'following-sibling::dd'

    @property
    def properties(self):
        """Return dict of stack properties from block."""
        _properties = {}
        for name_el in self.find_elements(self._property_name_locator):
            name = name_el.get_attribute('innerText')
            value_el = name_el.find_element(*self._property_value_locator)
            value = value_el.get_attribute('innerText')
            _properties[name] = value
        return _properties


@ui.register_ui(
    table_resource_topology=ui.Table(By.CSS_SELECTOR,
                                     '#heat_resource_topology'),
    stack_info_main=Info(By.XPATH, '//*[@id="stack_details"]'))
class PageStack(PageBase):
    """Stack page."""

    url = "/project/stacks/stack/{}"
