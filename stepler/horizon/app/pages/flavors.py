"""
------------
Flavors page
------------
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
    item_modify_access=ui.UI(By.CSS_SELECTOR, '[id$="action_projects"]'),
    item_update_metadata=ui.UI(By.CSS_SELECTOR,
                               '[id$="action_update_metadata"]'))
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for flavor row."""


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=DropdownMenu())
class RowFlavor(_ui.Row):
    """Row with flavor in flavors table."""


class TableFlavors(_ui.Table):
    """Flavors table."""

    columns = {'name': 2}
    row_cls = RowFlavor


@ui.register_ui(
    field_name=ui.TextField(By.NAME, 'name'),
    field_ram=ui.IntegerField(By.NAME, 'memory_mb'),
    field_root_disk=ui.IntegerField(By.NAME, 'disk_gb'),
    field_vcpus=ui.IntegerField(By.NAME, 'vcpus'))
class FormCreateFlavor(_ui.Form):
    """Form to create flavor."""

    submit_locator = By.CSS_SELECTOR, '[type="submit"]'


@ui.register_ui(
    button_add=ui.Button(By.CSS_SELECTOR, '.btn.btn-primary'))
class RowProject(_ui.Row):
    """Row with project."""


class ListProjects(ui.List):
    """List of projects."""

    row_cls = RowProject
    row_xpath = './ul[contains(@class, "btn-group")]'


@ui.register_ui(
    field_name=ui.TextField(By.NAME, 'name'),
    label_access=ui.UI(
        By.CSS_SELECTOR, '[data-target$="update_flavor_access"]'),
    label_info=ui.UI(By.CSS_SELECTOR, '[data-target$="update_info"]'),
    list_available_projects=ListProjects(
        By.CSS_SELECTOR, 'ul.available_members'))
class FormUpdateFlavor(_ui.Form):
    """Form to update flavor."""

    submit_locator = By.CSS_SELECTOR, '[type="submit"]'


@ui.register_ui(
    field_metadata_name=ui.UI(By.CSS_SELECTOR, '[ng-bind$="item.leaf.name"]'),
    field_metadata_value=ui.TextField(By.CSS_SELECTOR,
                                      '[ng-model$="item.leaf.value"]'))
class RowMetadata(_ui.Row):
    """Row of added metadata."""


class ListMetadata(ui.List):
    """List of added metadata."""

    row_cls = RowMetadata
    row_xpath = './li[contains(@ng-repeat, "item in existingList")]'


@ui.register_ui(
    button_add_metadata=ui.Button(By.CSS_SELECTOR, '[ng-click*="addCustom"]'),
    field_metadata_name=ui.TextField(By.NAME, 'customItem'),
    list_metadata=ListMetadata(By.CSS_SELECTOR, 'ul[ng-form$="metadataForm"]'))
class FormUpdateMetadata(_ui.Form):
    """Form to update image metadata."""

    submit_locator = By.CSS_SELECTOR, '.btn[ng-click$="modal.save()"]'
    cancel_locator = By.CSS_SELECTOR, '.btn[ng-click$="modal.cancel()"]'


@ui.register_ui(
    button_create_flavor=ui.Button(By.ID, 'flavors__action_create'),
    button_delete_flavors=ui.Button(By.ID, 'flavors__action_delete'),
    form_create_flavor=FormCreateFlavor(
        By.CSS_SELECTOR, '[action*="flavors/create"]'),
    form_update_flavor=FormUpdateFlavor(By.CSS_SELECTOR,
                                        '[action*="update"]'),
    form_update_metadata=FormUpdateMetadata(By.CSS_SELECTOR,
                                            'div.modal-content'),
    form_confirm_delete=_ui.Form(By.CSS_SELECTOR, 'div.modal-content'),
    table_flavors=TableFlavors(By.ID, 'flavors'))
class PageFlavors(PageBase):
    """Flavors page."""

    url = "/admin/flavors/"
    navigate_items = 'Admin', 'System', 'Flavors'
