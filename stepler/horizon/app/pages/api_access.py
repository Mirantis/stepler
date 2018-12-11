"""
---------------
API Access page
---------------
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
    field_username=ui.TextField(
        By.CSS_SELECTOR, '.form-group:nth-of-type(1) > input[type="text"]'),
    field_project_name=ui.TextField(
        By.CSS_SELECTOR, '.form-group:nth-of-type(2) > input[type="text"]'),
    field_project_id=ui.TextField(
        By.CSS_SELECTOR, '.form-group:nth-of-type(3) > input[type="text"]'),
    field_auth_url=ui.TextField(
        By.CSS_SELECTOR, '.form-group:nth-of-type(4) > input[type="text"]'))
class FormUserCredentials(_ui.Form):
    """Form with user credentials."""


@ui.register_ui(
    button_download_v2_file=ui.Button(
        By.ID, 'endpoints__action_download_openrc_v2'),
    button_download_ec2=ui.Button(
        By.ID, 'endpoints__action_download_ec2'),
    button_view_credentials=ui.Button(
        By.ID, 'endpoints__action_view_credentials'),
    button_download_rc_files=ui.Button(
        By.XPATH, '//div[contains(@class, "table_actions_menu")]'),
    button_download_v3_file=ui.Button(
        By.ID, 'endpoints__action_download_openrc'),
    form_user_credentials=FormUserCredentials(By.CSS_SELECTOR,
                                              'div.modal-content'),
    label_identity=ui.UI(
        By.CSS_SELECTOR, 'tr[data-display="keystone"] > td:nth-of-type(2)'),
    label_volume=ui.UI(
        By.CSS_SELECTOR, 'tr[data-display="cinderv3"] > td:nth-of-type(2)'))
class PageApiAccess(PageBase):
    """API Access page."""
    url = "/project/api_access/"
    navigate_items = "Project", "API Access"
