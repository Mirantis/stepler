"""
---------------
Containers page
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
    checkbox_public=_ui.CheckBox(By.NAME, 'public'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormCreateContainer(_ui.Form):
    """Form to create container."""


@ui.register_ui(
    button_delete_container=ui.Button(
        By.CSS_SELECTOR, '[ng-click*="deleteContainer"]'),
    label_created_date=ui.UI(
        By.CSS_SELECTOR, '.hz-object-timestamp .hz-object-val'),
    label_objects_count=ui.UI(
        By.CSS_SELECTOR, '.hz-object-count .hz-object-val'),
    label_size=ui.UI(
        By.CSS_SELECTOR, '.hz-object-size .hz-object-val'),
    link_public_url=ui.Link(
        By.CSS_SELECTOR, '.hz-object-link a[ng-show*="public_url"]'))
class RowContainer(_ui.Row):
    """Row with container."""


class ListContainers(ui.List):
    """List of containers."""

    row_cls = RowContainer
    row_xpath = ".//div[@ng-click='cc.selectContainer(container)']"


@ui.register_ui(item_delete=ui.UI(By.CSS_SELECTOR, '.text-danger'))
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for row with object."""


@ui.register_ui(
    button_delete=ui.Button(By.CSS_SELECTOR, 'button.btn-danger'),
    dropdown_menu=DropdownMenu(),
    link_folder=ui.Link(By.XPATH, './td//a'))
class RowObject(_ui.Row):
    """Row with object."""


class TableObjects(_ui.Table):
    """Table with objects."""

    columns = {'name': 1}
    row_cls = RowObject
    row_xpath = ('(.//tr[@ng-repeat])|(.//tr[@ng-repeat-start])|'
                 '(.//tr[@ng-repeat-end])')


@ui.register_ui(field_name=ui.TextField(By.NAME, 'name'))
class FormCreateFolder(_ui.Form):
    """Form to create folder."""


@ui.register_ui(
    field_file=ui.FileField(By.NAME, 'file'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormUploadFile(_ui.Form):
    """Form to upload file."""


@ui.register_ui(
    button_create_container=ui.Button(
        By.CSS_SELECTOR, 'button[ng-click="cc.createContainer()"]'),
    button_create_folder=ui.Button(
        By.XPATH, './/button[contains(., "Folder")]'),
    button_upload_file=ui.Button(
        By.XPATH, './/button[.//span[contains(@class, "fa-upload")]]'),
    form_create_container=FormCreateContainer(
        By.CSS_SELECTOR, 'div[ng-form="containerForm"]'),
    form_create_folder=FormCreateFolder(
        By.CSS_SELECTOR, 'div.modal-content'),
    form_upload_file=FormUploadFile(
        By.CSS_SELECTOR, 'div[ng-form="ctrl.form"]'),
    list_containers=ListContainers(
        By.CSS_SELECTOR, 'div.panel-group'),
    table_objects=TableObjects(By.CSS_SELECTOR, 'table.table-detail'))
class PageContainers(PageBase):
    """Containers Page."""

    url = "/project/containers/"
    navigate_items = 'Project', 'Object Store', 'Containers'
