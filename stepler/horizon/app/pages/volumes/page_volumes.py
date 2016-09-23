"""
Volumes page.

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
from .tab_backups import TabBackups
from .tab_snapshots import TabSnapshots
from .tab_volumes import TabVolumes


@ui.register_ui(
    label_backups=ui.UI(By.CSS_SELECTOR, '[data-target$="backups_tab"]'),
    label_snapshots=ui.UI(By.CSS_SELECTOR, '[data-target$="snapshots_tab"]'),
    label_volumes=ui.UI(By.CSS_SELECTOR, '[data-target$="volumes_tab"]'),
    tab_backups=TabBackups(),
    tab_snapshots=TabSnapshots(),
    tab_volumes=TabVolumes())
class PageVolumes(PageBase):
    """Volumes page."""

    url = "/project/volumes/"
    navigate_items = "Project", "Compute", "Volumes"
