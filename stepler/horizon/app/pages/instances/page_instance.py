"""
Instance page.

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

from ..base import PageBase


@ui.register_ui(label_name=ui.UI(By.CSS_SELECTOR, 'dd:nth-of-type(1)'))
class Info(ui.Block):
    """Instance info table."""


@ui.register_ui(
    info_instance=Info(By.CSS_SELECTOR,
                       'div.detail dl.dl-horizontal:nth-of-type(1)'))
class PageInstance(PageBase):
    """Instance page."""

    url = "/project/instances/{id}/"
