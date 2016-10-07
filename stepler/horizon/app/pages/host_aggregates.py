"""
--------------------
Host aggregates page
--------------------
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
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=_ui.DropdownMenu())
class RowHostAggregate(_ui.Row):
    """Row with host aggregate in host aggregates table."""


class TableHostAggregates(_ui.Table):
    """Host aggregates table."""

    columns = {'name': 2}
    row_cls = RowHostAggregate


@ui.register_ui(field_name=ui.TextField(By.NAME, 'name'))
class FormCreateHostAggregate(_ui.Form):
    """Form to create host aggregate."""

    submit_locator = By.CSS_SELECTOR, 'input[type="submit"]'


@ui.register_ui(
    button_create_host_aggregate=ui.Button(
        By.ID, 'host_aggregates__action_create'),
    button_delete_host_aggregates=ui.Button(
        By.ID, 'host_aggregates__action_delete'),
    form_create_host_aggregate=FormCreateHostAggregate(
        By.CSS_SELECTOR, '[action*="aggregates/create"]'),
    table_host_aggregates=TableHostAggregates(By.ID, 'host_aggregates'))
class PageHostAggregates(PageBase):
    """Host aggregates Page."""

    url = "/admin/aggregates/"
    navigate_items = 'Admin', 'System', 'Host Aggregates'
