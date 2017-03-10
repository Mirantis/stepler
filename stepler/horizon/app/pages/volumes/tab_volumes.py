"""
-----------
Volumes tab
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

from ..instances.page_instances import FormLaunchInstance


@ui.register_ui(
    field_name=ui.TextField(By.NAME, 'name'),
    field_description=ui.TextField(By.NAME, 'description'),
    field_size=ui.TextField(By.NAME, 'size'),
    combobox_source_type=_ui.combobox_by_label("Volume Source"),
    combobox_image_source=_ui.combobox_by_label("Use image as a source"),
    combobox_volume_source=_ui.combobox_by_label("Use a volume as source"),
    combobox_volume_type=_ui.combobox_by_label("Type"))
class FormCreateVolume(_ui.Form):
    """Form to create volume."""


@ui.register_ui(field_name=ui.TextField(By.NAME, 'name'))
class FormEditVolume(_ui.Form):
    """Form to edit volume."""


@ui.register_ui(
    item_change_volume_type=ui.UI(By.CSS_SELECTOR, '*[id$="action_retype"]'),
    item_create_backup=ui.UI(By.CSS_SELECTOR, '[id$="action_backups"]'),
    item_create_snapshot=ui.UI(By.CSS_SELECTOR, 'a[id$="action_snapshots"]'),
    item_create_transfer=ui.UI(By.CSS_SELECTOR,
                               '[id$="action_create_transfer"]'),
    item_extend_volume=ui.UI(By.CSS_SELECTOR, '*[id$="action_extend"]'),
    item_launch_volume_as_instance=ui.UI(By.CSS_SELECTOR,
                                         '*[id$="action_launch_volume_ng"]'),
    item_manage_attachments=ui.UI(By.CSS_SELECTOR,
                                  '[id$="action_attachments"]'),
    item_upload_to_image=ui.UI(By.CSS_SELECTOR,
                               '*[id$="action_upload_to_image"]'))
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for volume row."""


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=DropdownMenu(),
    link_volume=ui.UI(By.CSS_SELECTOR, 'td > a'))
class RowVolume(_ui.Row):
    """Volume row of volumes table."""

    transit_statuses = ('Attaching',
                        'Creating',
                        'Detaching',
                        'downloading',
                        'Extending',
                        'uploading')


class TableVolume(_ui.Table):
    """Volumes table."""

    columns = {'name': 2,
               'description': 3,
               'size': 4,
               'status': 5,
               'type': 6,
               'attached_to': 7}
    row_cls = RowVolume


@ui.register_ui(combobox_volume_type=_ui.combobox_by_label("Type"))
class FormChangeVolumeType(_ui.Form):
    """Form to change volume type."""


@ui.register_ui(field_image_name=ui.TextField(By.NAME, 'image_name'))
class FormUploadToImage(_ui.Form):
    """Form to upload volume to image."""


@ui.register_ui(field_new_size=ui.IntegerField(By.NAME, 'new_size'))
class FormExtendVolume(_ui.Form):
    """Form extend volume."""


@ui.register_ui(
    field_description=ui.TextField(By.NAME, 'description'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormCreateSnapshot(_ui.Form):
    """Form create volume snapshot."""


@ui.register_ui(
    detach_volume_button=ui.Button(By.CSS_SELECTOR, '[id$="action_detach"]'))
class RowAttachedInstance(_ui.Row):
    """Row with attached instance to volume."""


class TableAttachedInstances(_ui.Table):
    """Table of attached instances to volume."""

    columns = {'name': 2}
    row_cls = RowAttachedInstance


@ui.register_ui(
    combobox_instance=_ui.combobox_by_label("Attach to Instance"),
    table_instances=TableAttachedInstances(By.ID, 'attachments'))
class FormManageAttachments(_ui.Form):
    """Form to manage volume attachments."""


@ui.register_ui(field_name=ui.TextField(By.NAME, 'name'))
class FormCreateTransfer(_ui.Form):
    """Form to create transfer."""


@ui.register_ui(
    field_transfer_id=ui.TextField(By.NAME, 'transfer_id'),
    field_transfer_key=ui.TextField(By.NAME, 'auth_key'))
class FormAcceptTransfer(_ui.Form):
    """Form to accept transfer."""


@ui.register_ui(
    field_container=ui.TextField(By.NAME, 'container_name'),
    field_description=ui.TextField(By.NAME, 'description'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormCreateBackup(_ui.Form):
    """Form to create volume backup."""


@ui.register_ui(
    button_accept_transfer=ui.Button(By.ID, 'volumes__action_accept_transfer'),
    button_create_volume=ui.Button(By.ID, 'volumes__action_create'),
    button_delete_volumes=ui.Button(By.ID, 'volumes__action_delete'),
    form_accept_transfer=FormAcceptTransfer(
        By.CSS_SELECTOR, 'form[action*="/accept_transfer"]'),
    form_change_volume_type=FormChangeVolumeType(By.CSS_SELECTOR,
                                                 'form[action*="/retype"]'),
    form_create_backup=FormCreateBackup(
        By.CSS_SELECTOR, 'form[action*="/create_backup"]'),
    form_create_snapshot=FormCreateSnapshot(
        By.CSS_SELECTOR, 'form[action*="/create_snapshot"]'),
    form_create_transfer=FormCreateTransfer(
        By.CSS_SELECTOR, 'form[action*="/create_transfer"]'),
    form_create_volume=FormCreateVolume(By.CSS_SELECTOR,
                                        'form[action*="volumes/create"]'),
    form_edit_volume=FormEditVolume(By.CSS_SELECTOR,
                                    'form[action*="/update"]'),
    form_extend_volume=FormExtendVolume(By.CSS_SELECTOR,
                                        'form[action*="/extend"]'),
    form_launch_instance=FormLaunchInstance(
        By.CSS_SELECTOR,
        'wizard[ng-controller="LaunchInstanceWizardController"]'),
    form_manage_attachments=FormManageAttachments(By.CSS_SELECTOR,
                                                  'div.modal-content'),
    form_upload_to_image=FormUploadToImage(By.CSS_SELECTOR,
                                           'form[action*="/upload_to_image"]'),
    table_volumes=TableVolume(By.ID, 'volumes'))
class TabVolumes(_ui.Tab):
    """Volumes tab."""
