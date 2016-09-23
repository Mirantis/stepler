"""
Admin volumes page.

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
from .tab_admin_volumes import TabAdminVolumes
from .tab_volume_types import TabVolumeTypes


@ui.register_ui(
    label_volumes=ui.UI(By.CSS_SELECTOR, '[data-target$="volumes_tab"]'),
    label_volume_types=ui.UI(By.CSS_SELECTOR,
                             '[data-target$="volume_types_tab"]'),
    tab_volumes=TabAdminVolumes(),
    tab_volume_types=TabVolumeTypes())
class PageAdminVolumes(PageBase):
    """Admin volumes page."""

    url = "/admin/volumes/"
    navigate_items = "Admin", "System", "Volumes"
