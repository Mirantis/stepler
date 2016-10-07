"""
-----------
Routers tab
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

from .base import PageBase


@ui.register_ui(
    combobox_admin_state=ui.ComboBox(By.NAME, 'admin_state_up'),
    combobox_external_network=ui.ComboBox(By.NAME, 'external_network'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormCreateRouter(_ui.Form):
    """Form to create router."""


@ui.register_ui(dropdown_menu=_ui.DropdownMenu())
class RowRouter(_ui.Row):
    """Router row."""


class TableRouters(_ui.Table):
    """Routers table."""

    columns = {'name': 2}
    row_cls = RowRouter


@ui.register_ui(
    button_create_router=ui.Button(By.ID, 'routers__action_create'),
    form_create_router=FormCreateRouter(By.ID, 'create_router_form'),
    table_routers=TableRouters(By.ID, 'routers'))
class PageRouters(PageBase):
    """Routers page."""

    url = "/project/routers/"
    navigate_items = "Project", "Network", "Routers"
