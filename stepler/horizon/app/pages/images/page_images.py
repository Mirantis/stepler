"""
Images page.

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

from ..base import PageBase
from ..instances.page_instances import FormLaunchInstance
from ..volumes.tab_volumes import FormCreateVolume


@ui.register_ui(
    item_create_volume=ui.UI(
        By.CSS_SELECTOR, '[id$="action_create_volume_from_image"]'),
    item_update_metadata=ui.UI(
        By.CSS_SELECTOR, '[id$="action_update_metadata"]'))
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for image row."""


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=DropdownMenu(),
    link_image=ui.Link(By.CSS_SELECTOR, 'td > a'))
class RowImage(_ui.Row):
    """Row with image in images table."""

    transit_statuses = ('Queued', 'Saving')


class TableImages(_ui.Table):
    """Images table."""

    columns = {'name': 2, 'type': 3, 'status': 4, 'format': 7}
    row_cls = RowImage


@ui.register_ui(
    checkbox_protected=_ui.CheckBox(By.NAME, 'protected'),
    combobox_disk_format=_ui.ComboBox(
        By.XPATH,
        './/div[contains(@class, "themable-select") and '
        'select[@name="disk_format"]]'),
    combobox_source_type=ui.ComboBox(By.NAME, 'source_type'),
    field_image_file=ui.TextField(By.NAME, 'image_file'),
    field_image_url=ui.TextField(By.NAME, 'image_url'),
    field_min_disk=ui.TextField(By.NAME, 'minimum_disk'),
    field_min_ram=ui.TextField(By.NAME, 'minimum_ram'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormCreateImage(_ui.Form):
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
    list_metadata=ListMetadata(By.CSS_SELECTOR, 'ul[ng-form$="metadataForm"]'))
class FormUpdateMetadata(_ui.Form):
    """Form to update image metadata."""

    submit_locator = By.CSS_SELECTOR, '.btn[ng-click$="modal.save()"]'
    cancel_locator = By.CSS_SELECTOR, '.btn[ng-click$="modal.cancel()"]'


@ui.register_ui(
    checkbox_protected=_ui.CheckBox(By.NAME, 'protected'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormUpdateImage(_ui.Form):
    """Form to update image."""


@ui.register_ui(
    button_create_image=ui.Button(By.ID, 'images__action_create'),
    button_delete_images=ui.Button(By.ID, 'images__action_delete'),
    button_public_images=ui.Button(By.CSS_SELECTOR, 'button[value="public"]'),
    form_create_image=FormCreateImage(By.ID, 'create_image_form'),
    form_create_volume=FormCreateVolume(
        By.CSS_SELECTOR, '[action*="volumes/create"]'),
    form_launch_instance=FormLaunchInstance(
        By.CSS_SELECTOR,
        'wizard[ng-controller="LaunchInstanceWizardController"]'),
    form_update_image=FormUpdateImage(By.ID, 'update_image_form'),
    form_update_metadata=FormUpdateMetadata(By.CSS_SELECTOR,
                                            'div.modal-content'),
    table_images=TableImages(By.ID, 'images'))
class PageImages(PageBase):
    """Images Page."""

    url = "/project/images/"
    navigate_items = 'Project', 'Compute', 'Images'
