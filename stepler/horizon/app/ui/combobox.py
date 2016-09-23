"""
Themable combobox.

@author: chipiga86@gmail.com
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
from pom.utils import timeit
from selenium.webdriver.common.by import By
from waiting import wait


# TODO(schipiga): maybe need refactoring
class ComboBox(ui.Block):
    """Themable combobox."""

    value_locator = By.CSS_SELECTOR, 'span.dropdown-title'
    toggle_locator = By.CSS_SELECTOR, 'span.fa-caret-down'
    values_container_locator = By.CSS_SELECTOR, 'ul.dropdown-menu'
    values_locator = By.CSS_SELECTOR, 'ul.dropdown-menu > li > a'

    @property
    @timeit
    @ui.wait_for_presence
    def value(self):
        """Combobox value."""
        element = self.find_element(self.value_locator)
        return element.get_attribute('innerHTML').strip()

    @value.setter
    @timeit
    @ui.wait_for_presence
    def value(self, value):
        """Set combobox value."""
        if value in self.value:
            return

        dropdown_button = self.find_element(self.toggle_locator)
        dropdown_button.click()

        values_container = self.find_element(self.values_container_locator)
        wait(values_container.is_displayed,
             timeout_seconds=5, sleep_seconds=0.1)

        value_elements = self.find_elements(self.values_locator)
        for element in value_elements:

            if value in element.get_attribute('innerHTML').strip():
                element.click()

                wait(lambda: not values_container.is_displayed(),
                     timeout_seconds=5, sleep_seconds=0.1)

                assert value in self.value
                break
        else:
            raise Exception(
                '{!r} is absent among {} values'.format(value, self))

    @property
    @timeit
    @ui.wait_for_presence
    def values(self):
        """Combobox values."""
        _values = []
        elements = self.find_elements(self.values_locator)
        for element in elements:
            value = element.get_attribute('innerHTML').strip()
            _values.append(value)
        return _values
