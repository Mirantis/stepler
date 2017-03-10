"""Themable file field."""

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


class FileField(ui.Block):
    """Themable file field."""

    input_locator = By.CSS_SELECTOR, 'input[type="file"]'

    @property
    def file_input(self):
        return self.webdriver.find_element(*self.input_locator)

    @property
    @ui.wait_for_presence
    def value(self):
        """Get file path."""
        return self.file_input.value

    @value.setter
    @ui.wait_for_presence
    def value(self, value):
        """Set file to upload."""
        self.file_input.send_keys(value)
