"""
----------
Image page
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
    """Image info table."""

    _property_name_locator = By.TAG_NAME, 'dt'
    _property_value_locator = By.XPATH, 'following-sibling::dd'

    @property
    def properties(self):
        """Return dict of image properties from block."""
        _properties = {}
        for name_el in self.find_elements(self._property_name_locator):
            name = name_el.get_attribute('innerText')
            value_el = name_el.find_element(*self._property_value_locator)
            value = value_el.get_attribute('innerText')
            _properties[name] = value
        return _properties


@ui.register_ui(
    image_info_main=Info(By.XPATH,
                         './/div[./h3[.="Image"]]'),
    image_info_custom=Info(By.XPATH,
                           './/div[./h3[.="Custom Properties"]]'),
    label_name=ui.UI(By.CSS_SELECTOR, '.h1'))
class PageImage(PageBase):
    """Image page."""

    url = "/project/images/{id}/"
