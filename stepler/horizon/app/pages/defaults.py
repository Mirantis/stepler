"""
-------------
Defaults page
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


@ui.register_ui(
    field_volumes=ui.IntegerField(By.NAME, 'volumes'),
    field_key_pairs=ui.IntegerField(By.NAME, 'key_pairs'),
    field_instances=ui.IntegerField(By.NAME, 'instances'))
class FormUpdateDefaults(_ui.Form):
    """Form to update defaults."""


@ui.register_ui(
    button_update_defaults=ui.Button(By.ID, 'quotas__action_update_defaults'),
    form_update_defaults=FormUpdateDefaults(
        By.CSS_SELECTOR, '[action*="update_defaults"]'),
    label_key_pairs=ui.UI(
        By.XPATH, '//tr[@id="quotas__row__key_pairs"]/td[2]'),
    label_volumes=ui.UI(By.XPATH, '//tr[@id="quotas__row__volumes"]/td[2]'),
    label_instances=ui.UI(By.XPATH,
                          '//tr[@id="quotas__row__instances"]/td[2]'))
class PageDefaults(PageBase):
    """Defaults page."""

    url = "/admin/defaults/"
    navigate_items = "Admin", "System", "Defaults"
