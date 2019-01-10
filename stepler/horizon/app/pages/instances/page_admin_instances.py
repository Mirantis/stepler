"""
--------------
Admin instances page
--------------
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
    item_delete=ui.UI(By.CSS_SELECTOR, '*[id*="action_delete"]'))
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for instance row."""


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=DropdownMenu(),
    link_instance=ui.Link(By.CSS_SELECTOR, 'td > a'))
class RowInstance(_ui.Row):
    """Row with instance."""

    transit_statuses = ('Build',)


class TableInstances(_ui.Table):
    """Instances table."""

    columns = {'name': 4, 'status': 8}
    row_cls = RowInstance
    row_xpath = '//tr[contains(@id, "instances__row")]'


@ui.register_ui(
    button_delete_instances=ui.Button(By.ID, 'instances__action_delete'),
    button_filter_instances=ui.Button(
        By.ID, 'instances__action_filter_admin_instances'),
    field_filter_instances=ui.TextField(
        By.NAME, 'instances__filter_admin_instances__q'),
    combobox_filter_target=ui.ComboBox(
        By.NAME, 'instances__filter_admin_instances__q_field'),
    table_instances=TableInstances(By.ID, 'instances'))
class PageAdminInstances(PageBase):
    """Admin instances page."""

    url = "/admin/instances/"
    navigate_items = 'Admin', 'Compute', "Instances"

    def item_instance_parameter(self, par):
        """Select parameter for filtering."""
        self.webelement.find_elements_by_xpath(
            "//*[contains(@class, 'themable-select')]")[0].click()
        return self.webelement.find_elements_by_xpath(
            "//*[contains(@class, "
            "'themable-select')]//a[@data-select-value='{}']".format(par))[0]
