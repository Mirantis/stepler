"""
-------------
Snapshots tab
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

from .tab_volumes import FormCreateSnapshot


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=_ui.DropdownMenu())
class RowSnapshot(_ui.Row):
    """Volume snapshot row of volume snapshots table."""
    transit_statuses = ('Creating',)


@ui.register_ui(
    link_next=ui.UI(By.CSS_SELECTOR, 'a[href^="?snapshot_marker="]'),
    link_prev=ui.UI(By.CSS_SELECTOR, 'a[href^="?prev_snapshot_marker="]'))
class TableSnapshots(_ui.Table):
    """Volume snapshots table."""

    columns = {'name': 2,
               'description': 3,
               'size': 4,
               'status': 5,
               'volume_name': 6}
    row_cls = RowSnapshot


@ui.register_ui(
    combobox_source=ui.ComboBox(By.NAME, 'snapshot_source'),
    combobox_type=ui.ComboBox(By.NAME, 'type'),
    field_description=ui.TextField(By.NAME, 'description'),
    field_name=ui.TextField(By.NAME, 'name'),
    field_size=ui.IntegerField(By.NAME, 'size'))
class FormCreateVolume(_ui.Form):
    """Form to create volume from snapshot."""


@ui.register_ui(
    button_delete_snapshots=ui.Button(By.ID,
                                      'volume_snapshots__action_delete'),
    form_create_volume=FormCreateVolume(By.CSS_SELECTOR,
                                        'form[action*="volumes/create"]'),
    form_edit_snapshot=FormCreateSnapshot(By.ID, 'update_snapshot_form'),
    table_snapshots=TableSnapshots(By.ID, 'volume_snapshots'))
class TabSnapshots(_ui.Tab):
    """Volume snapshots tab."""
