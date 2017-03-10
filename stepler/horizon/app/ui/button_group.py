"""Button group."""

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


class ButtonGroup(ui.Block):
    """Bootstrap button group."""

    values_locator = By.CSS_SELECTOR, ".btn"
    active_value_locator = By.CSS_SELECTOR, ".btn.active"

    @property
    @ui.wait_for_presence
    def value(self):
        """Button group value."""
        element = self.find_element(self.active_value_locator)
        return element.get_attribute('innerText').strip()

    @value.setter
    @ui.wait_for_presence
    def value(self, value):
        """Set button group value."""
        if value == self.value:
            return

        value_elements = self.find_elements(self.values_locator)
        for element in value_elements:

            if value == element.get_attribute('innerText').strip():
                # Scroll to element
                element.click()

                assert value == self.value
                break
        else:
            raise Exception(
                '{!r} is absent among {} values'.format(value, self))

    @property
    @ui.wait_for_presence
    def values(self):
        """Button group values."""
        _values = []
        elements = self.find_elements(self.values_locator)
        for element in elements:
            value = element.get_attribute('innerText').strip()
            _values.append(value)
        return _values


def button_group_by_label(label):
    """Return ButtonGroup instance with correct XPATH selector by label."""
    return ButtonGroup(By.XPATH, './/*[contains(@class, "form-group") and '
                       './label[contains(., "{}")]]'
                       '//*[contains(@class, "btn-group")]'.format(label))
