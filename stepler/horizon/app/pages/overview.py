"""
-------------
Overview page
-------------
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

from stepler.horizon.app import ui as _ui

from .base import PageBase


class RowAvailableResources(_ui.Form):
    """Overview resources."""
    def value(self, name):
        return self.webelement.find_element(By.XPATH, (
            "//*[contains(@class, 'd3_quota_bar')][./*[contains("
            "., '{}')]]//span").format(name)).text


@ui.register_ui(row_avaible_resource=RowAvailableResources(By.ID,
                                                           'content_body'))
class PageOverview(PageBase):
    """Overview page."""
    url = "/project/"
    navigate_items = "Project", "Compute", "Overview"
