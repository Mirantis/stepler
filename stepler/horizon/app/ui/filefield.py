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

import os

from pom import ui
from selenium.webdriver.common.by import By


@ui.register_ui(
    browse_button=ui.Button(By.TAG_NAME, 'button'),
    field_input=ui.UI(By.TAG_NAME, 'input'),
)
class FileField(ui.Block):
    """Themable file field."""

    @property
    @ui.wait_for_presence
    def value(self):
        """Get file path."""
        return self.field_input.value

    @value.setter
    @ui.wait_for_presence
    def value(self, value):
        """Set file to upload."""
        self.browse_button.click()
        # Choose file with opened dialog
        os.system('xdotool type --clearmodifiers "{}"'.format(value))
        os.system('xdotool key Return')
        assert value.endswith(self.value)
