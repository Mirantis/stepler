"""
Settings page.

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
    combobox_lang=ui.ComboBox(By.NAME, 'language'),
    combobox_timezone=ui.ComboBox(By.NAME, 'timezone'),
    field_items_per_page=ui.IntegerField(By.NAME, 'pagesize'),
    field_instance_log_length=ui.IntegerField(By.NAME, 'instance_log_length'))
class FormSettings(_ui.Form):
    """Form of settings."""


@ui.register_ui(form_settings=FormSettings(By.ID, 'user_settings_modal'))
class PageSettings(PageBase):
    """Settings page."""

    url = "/settings/"


@ui.register_ui(
    field_confirm_password=ui.TextField(By.NAME, 'confirm_password'),
    field_current_password=ui.TextField(By.NAME, 'current_password'),
    field_new_password=ui.TextField(By.NAME, 'new_password'))
class FormChangePassword(_ui.Form):
    """Form to change user password."""


@ui.register_ui(
    form_change_password=FormChangePassword(By.ID, 'change_password_modal'))
class PagePassword(PageBase):
    """Page to change user password."""

    url = "/settings/password/"
