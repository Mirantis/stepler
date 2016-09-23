"""
Defaults page.

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

from stepler.horizon.app import ui as _ui

from .base import PageBase


@ui.register_ui(
    field_volumes=ui.IntegerField(By.NAME, 'volumes'))
class FormUpdateDefaults(_ui.Form):
    """Form to update defaults."""


@ui.register_ui(
    button_update_defaults=ui.Button(By.ID, 'quotas__action_update_defaults'),
    form_update_defaults=FormUpdateDefaults(
        By.CSS_SELECTOR, '[action*="update_defaults"]'),
    label_volumes=ui.UI(
        By.CSS_SELECTOR, 'tr[data-display="volumes"] > td:nth-of-type(2)'))
class PageDefaults(PageBase):
    """Defaults page."""

    url = "/admin/defaults/"
    navigate_items = "Admin", "System", "Defaults"
