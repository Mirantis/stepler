"""
-------------------
Admin networks page
-------------------
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
    dropdown_menu=_ui.DropdownMenu(),
    link_network=ui.UI(By.CSS_SELECTOR, 'td.anchor > a'))
class RowNetwork(_ui.Row):
    """Row with network in networks table."""


class TableNetworks(_ui.Table):
    """Networks table."""

    columns = {'name': 3}
    row_cls = RowNetwork


@ui.register_ui(
    checkbox_shared=_ui.CheckBox(By.NAME, 'shared'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormUpdateNetwork(_ui.Form):
    """Form to update network as admin."""


@ui.register_ui(
    button_delete_networks=ui.Button(By.ID, 'networks__action_delete'),
    button_filter_networks=ui.Button(By.CLASS_NAME, 'fa-search'),
    field_filter_networks=ui.TextField(By.NAME, 'networks__filter__q'),
    form_update_network=FormUpdateNetwork(By.ID, 'update_network_form'),
    table_networks=TableNetworks(By.ID, 'networks'))
class PageAdminNetworks(PageBase):
    """Admin networks page."""

    url = "/admin/networks/"
    navigate_items = 'Admin', 'System', 'Networks'
