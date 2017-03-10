"""Items list filters."""

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
from selenium.webdriver.common.keys import Keys


class Dropdown(ui.Block):
    """Search bar dropdown list."""
    item_locator = By.TAG_NAME, 'a'

    @property
    def items(self):
        return self.find_elements(self.item_locator)

    @property
    def names(self):
        _names = []
        for item in self.items:
            _names.append(item.get_attribute('innerText').strip())
        return _names

    def select(self, name):
        for item in self.items:
            if item.get_attribute('innerText').strip() == name:
                item.click()
                break
        else:
            raise "Element with {} not found on {!r}".format(name, self)


@ui.register_ui(
    cancel_link=ui.UI(By.CSS_SELECTOR, 'a.remove'),
    value=ui.UI(By.CSS_SELECTOR, '.magic-search-result-string'),
)
class FilterItem(ui.Block):
    """Filter item"""
    name_locator = By.CSS_SELECTOR, '.magic-search-result-title'

    @property
    def name(self):
        """"""
        el = self.find_element(self.name_locator)
        return el.get_attribute('innerText').strip()


@ui.register_ui(
    input=ui.UI(By.TAG_NAME, 'input'),
    dropdown=Dropdown(By.CSS_SELECTOR, 'ul.dropdown-menu'))
class SearchBar(ui.Block):
    """Search bar."""

    items_locator = By.CSS_SELECTOR, 'span.item'

    item_cls = FilterItem

    def item(self, name):
        selector = './/*[contains(., "{}:")]'.format(name)
        item = self.item_cls(By.XPATH, selector)
        item.container = self
        return item

    def apply(self, name, value):
        """Set filter with ``name`` to ``value``"""
        self.input.click()
        self.dropdown.wait_for_presence()

        self.dropdown.select(name)
        if self.dropdown.is_present:
            self.dropdown.select(value)
        else:
            self.input.send_keys(name, Keys.ENTER)
        self.item(name).wait_for_presence()

    def clear(self, name):
        """"""
        item = self.item(name)
        item.cancel_link.click()
        self.item(name).wait_for_absence()
