"""
Access & security page.

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
from .tab_api_access import TabApiAccess
from .tab_floating_ips import TabFloatingIPs
from .tab_keypairs import TabKeypairs
from .tab_security_groups import TabSecurityGroups


@ui.register_ui(
    label_api_access=ui.UI(
        By.CSS_SELECTOR, '[data-target$="api_access_tab"]'),
    label_floating_ips=ui.UI(
        By.CSS_SELECTOR, '[data-target$="floating_ips_tab"]'),
    label_keypairs=ui.UI(
        By.CSS_SELECTOR, '[data-target$="keypairs_tab"]'),
    label_security_groups=ui.UI(
        By.CSS_SELECTOR, '[data-target$="security_groups_tab"]'),
    tab_api_access=TabApiAccess(),
    tab_floating_ips=TabFloatingIPs(),
    tab_keypairs=TabKeypairs(),
    tab_security_groups=TabSecurityGroups())
class PageAccess(PageBase):
    """Access & security page."""

    url = "/project/access_and_security/"
    navigate_items = "Project", "Compute", "Access & Security"
