"""
-----------------
Manage rules page
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

from ..base import PageBase


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=_ui.DropdownMenu())
class RowRules(_ui.Row):
    """User row of rules table."""


class TableManageRules(_ui.Table):
    """Manage rules table."""

    columns = {'port_range': 5}
    row_cls = RowRules


@ui.register_ui(
    field_port=ui.TextField(By.NAME, 'port'))
class FormAddRules(_ui.Form):
    """Form to add rules."""


@ui.register_ui(
    button_add_rule=ui.Button(By.ID, 'rules__action_add_rule'),
    button_delete_rules=ui.Button(By.ID, 'rules__action_delete'),
    form_add_rule=FormAddRules(By.ID, 'create_security_group_rule_form'),
    table_rules=TableManageRules(By.ID, 'rules'))
class PageManageRules(PageBase):
    """Manage rules page."""

    url = "/project/access_and_security/security_groups/{id}/"
