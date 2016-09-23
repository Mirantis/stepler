"""
Tab component.

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

from .initiated_ui import InitiatedUI


class Tab(ui.Block, InitiatedUI):
    """Tab component."""

    def __init__(self, *args, **kwgs):
        """Constructor.

        It has predefined locator.
        """
        super(Tab, self).__init__(*args, **kwgs)
        self.locator = By.TAG_NAME, 'body'
