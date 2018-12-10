"""
-------------
Keypairs page
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


@ui.register_ui(field_name=ui.TextField(By.NAME, 'name'),
                button_create_keypair=ui.Button(
                    By.CSS_SELECTOR, '[ng-click*="ctrl.generate()"]'),
                button_copy_keypair=ui.Button(
                    By.CSS_SELECTOR, '[ng-click*="ctrl.copyPrivateKey()"]'))
class FormCreateKeypair(_ui.Form):
    """Form to create keypair."""
    submit_locator = By.CSS_SELECTOR, '[ng-click*="ctrl.submit()"]'


@ui.register_ui(
    button_delete_keypair=ui.Button(By.CSS_SELECTOR, '[id*="action_delete"]'),
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'))
class RowKeypair(_ui.Row):
    """Row of keypair in keypairs table."""


class TableKeypairs(_ui.Table):
    """Keypairs table."""

    columns = {'name': 2}
    row_cls = RowKeypair


@ui.register_ui(field_name=ui.TextField(By.NAME, 'name'),
                field_public_key=ui.TextField(By.NAME, 'public_key'))
class FormImportKeypair(_ui.Form):
    """Form to import keypair."""


@ui.register_ui(
    button_create_keypair=ui.Button(
        By.ID, 'keypairs__action_create-keypair-ng'),
    button_delete_keypairs=ui.Button(By.ID, 'keypairs__action_delete'),
    button_import_keypair=ui.Button(By.ID, 'keypairs__action_import'),
    form_confirm_delete=_ui.Form(By.CSS_SELECTOR, 'div.modal-content'),
    form_create_keypair=FormCreateKeypair(
        By.CSS_SELECTOR, 'div.modal-content'),
    form_import_keypair=FormImportKeypair(
        By.XPATH, '//*[@action="/project/key_pairs/import/"]'),
    table_keypairs=TableKeypairs(By.ID, 'keypairs'))
class PageKeypairs(PageBase):
    """Keypairs page."""
    url = "project/key_pairs/"
    navigate_items = "Project", "Compute", "Key Pairs"
