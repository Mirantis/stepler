"""
-----------------
Admin volumes tab
-----------------
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


@ui.register_ui(
    item_update_volume_status=ui.UI(
        By.CSS_SELECTOR, '*[id*="action_update_status"]'),
    item_migrate_volume=ui.UI(By.CSS_SELECTOR, '[id$="action_migrate"]'))
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for admin volume row."""


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=DropdownMenu())
class RowVolume(_ui.Row):
    """Row of admin volume."""


class TableVolumes(_ui.Table):
    """Admin volumes table."""

    columns = {'project': 2,
               'host': 3,
               'name': 4,
               'size': 5,
               'status': 6,
               'type': 7}
    row_cls = RowVolume

    def values(self):
        """List contains names of volumes in admin volumes table."""
        return self.webelement.find_elements(By.TAG_NAME, 'a')


@ui.register_ui(combobox_status=_ui.combobox_by_label("Status"))
class FormUpdateVolumeStatus(_ui.Form):
    """Form to update volume status."""


@ui.register_ui(
    combobox_destination_host=_ui.combobox_by_label("Destination Host"),
    field_current_host=ui.TextField(By.NAME, 'current_host'))
class FormMigrateVolume(_ui.Form):
    """Form to migrate volume."""


@ui.register_ui(
    table_volumes=TableVolumes(By.CSS_SELECTOR, 'table[id="volumes"]'),
    form_update_volume_status=FormUpdateVolumeStatus(
        By.CSS_SELECTOR, 'form[action*="/update_status"]'),
    form_migrate_volume=FormMigrateVolume(By.ID, 'migrate_volume_modal'))
class TabAdminVolumes(_ui.Tab):
    """Admin volumes tab."""
