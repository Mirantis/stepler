"""
-----------
Images page
-----------
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

from ..base import PageBase
from ..instances.page_instances import FormLaunchInstance


@ui.register_ui(
    item_create_volume=ui.UI(By.XPATH, './/a[contains(., "Create Volume")]'),
    item_update_metadata=ui.UI(By.XPATH,
                               './/a[contains(., "Update Metadata")]'),
    item_delete=ui.UI(By.CSS_SELECTOR, '*[id*="action_delete"]'),
    item_edit=ui.UI(By.XPATH, './/a[contains(., "Edit Image")]'), )
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for image row."""


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=DropdownMenu(),
    link_image=ui.Link(By.CSS_SELECTOR, 'td a'))
class RowImage(_ui.Row):
    """Row with image in images table."""

    transit_statuses = ('Queued', 'Saving')


class TableImages(_ui.Table):
    """Images table."""

    columns = {'name': 2}
    row_cls = RowImage


@ui.register_ui(
    button_group_protected=_ui.button_group_by_label("Protected"),
    field_min_disk=ui.TextField(By.NAME, 'min_disk'),
    field_min_ram=ui.TextField(By.NAME, 'min_ram'),
    field_description=ui.TextField(By.NAME, 'description'),
    field_name=ui.TextField(By.NAME, 'name'),
    combobox_disk_format=ui.ComboBox(By.NAME, 'format'), )
class FormImage(_ui.Form):
    """Base image form."""
    submit_locator = By.CSS_SELECTOR, '.modal-footer .btn.btn-primary'


@ui.register_ui(
    button_group_source_type=_ui.button_group_by_label("Source Type"),
    field_image_file=_ui.FileField(By.XPATH,
                                   './/*[contains(@class, "form-group") and '
                                   './label[contains(., "File")]]'
                                   '//*[contains(@class, "input-group")]'),
    field_image_url=ui.TextField(By.NAME, 'image_url'), )
class FormCreateImage(FormImage):
    """Form to create image."""


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
    existing_metadata_filter=ui.TextField(
        By.CSS_SELECTOR, '[ng-model="ctrl.filterText.existing"]'),
    button_delete_metadata=ui.Button(By.CSS_SELECTOR, 'a.btn > span.fa-minus'),
    list_metadata=ListMetadata(By.CSS_SELECTOR, 'ul[ng-form$="metadataForm"]'))
class FormUpdateMetadata(_ui.Form):
    """Form to update image metadata."""

    submit_locator = By.CSS_SELECTOR, '.btn[ng-click$="modal.save()"]'
    cancel_locator = By.CSS_SELECTOR, '.btn[ng-click$="modal.cancel()"]'


class FormUpdateImage(FormImage):
    """Form to update image."""


@ui.register_ui(
    field_name=ui.TextField(By.CSS_SELECTOR, 'input[ng-model$=".name"]'),
    field_description=ui.TextField(By.CSS_SELECTOR,
                                   'input[ng-model$=".description"]'),
    field_size=ui.TextField(By.CSS_SELECTOR, 'input[ng-model$=".size"]'),
    combobox_volume_type=ui.ComboBox(By.CSS_SELECTOR,
                                     'input[ng-model$=".volumeType"]'))
class FormCreateVolume(_ui.Form):
    """Form to create volume."""


@ui.register_ui(
    button_create_image=ui.Button(By.XPATH,
                                  './/button[contains(., "Create Image")]'),
    button_delete_images=ui.Button(By.XPATH,
                                   './/button[contains(., "Delete Images")]'),
    button_public_images=ui.Button(By.CSS_SELECTOR, 'button[value="public"]'),
    form_create_image=FormCreateImage(By.XPATH, './/*[@ng-form="wizardForm"]'),
    form_create_volume=FormCreateVolume(By.XPATH,
                                        './/*[@ng-form="wizardForm"]'),
    form_launch_instance=FormLaunchInstance(
        By.CSS_SELECTOR,
        'wizard[ng-controller="LaunchInstanceWizardController"]'),
    form_update_image=FormUpdateImage(By.XPATH, './/*[@ng-form="wizardForm"]'),
    form_update_metadata=FormUpdateMetadata(By.CSS_SELECTOR,
                                            'div.modal-content'),
    table_images=TableImages(By.ID, 'images'),
    search_bar=_ui.SearchBar(By.CSS_SELECTOR, '.magic-search-bar'))
class PageImages(PageBase):
    """Images Page."""

    url = "/project/images/"
    navigate_items = 'Project', 'Compute', 'Images'
