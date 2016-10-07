"""
-----------
Backups tab
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


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=_ui.DropdownMenu())
class RowBackup(_ui.Row):
    """Volume backup row of volume backups table."""


@ui.register_ui(
    link_next=ui.UI(By.CSS_SELECTOR, 'a[href^="?backup_marker="]'),
    link_prev=ui.UI(By.CSS_SELECTOR, 'a[href^="?prev_backup_marker="]'))
class TableBackups(_ui.Table):
    """Volume backups table."""

    columns = {'name': 2,
               'description': 3,
               'size': 4,
               'status': 5,
               'volume_name': 6}
    row_cls = RowBackup


@ui.register_ui(
    button_delete_backups=ui.Button(By.ID, 'volume_backups__action_delete'),
    table_backups=TableBackups(By.ID, 'volume_backups'))
class TabBackups(_ui.Tab):
    """Volume backups tab."""
