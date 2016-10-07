"""
-------------
Networks page
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

from ..base import PageBase


@ui.register_ui(
    item_add_subnet=ui.UI(By.CSS_SELECTOR, '[id$="action_subnet"]'))
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for network row."""


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=DropdownMenu())
class RowNetwork(_ui.Row):
    """Row with network in networks table."""


class TableNetworks(_ui.Table):
    """Networks table."""

    columns = {'name': 2, 'shared': 4}
    row_cls = RowNetwork


@ui.register_ui(
    button_next=ui.Button(By.CSS_SELECTOR, '.button-next'),
    checkbox_create_subnet=_ui.CheckBox(By.NAME, 'with_subnet'),
    checkbox_shared=_ui.CheckBox(By.NAME, 'shared'),
    field_gateway_ip=ui.TextField(By.NAME, 'gateway_ip'),
    field_name=ui.TextField(By.NAME, 'net_name'),
    field_network_address=ui.TextField(By.NAME, 'cidr'),
    field_subnet_name=ui.TextField(By.NAME, 'subnet_name'))
class FormCreateNetwork(_ui.Form):
    """Form to create network."""

    submit_locator = By.CSS_SELECTOR, '.btn.btn-primary.button-final'
    cancel_locator = By.CSS_SELECTOR, '.btn.btn-default.cancel'


@ui.register_ui(
    button_next=ui.Button(By.CSS_SELECTOR, '.button-next'),
    field_name=ui.TextField(By.NAME, 'subnet_name'),
    field_network_address=ui.TextField(By.NAME, 'cidr'))
class FormAddSubnet(_ui.Form):
    """Form to add subnet."""

    submit_locator = By.CSS_SELECTOR, '.btn.btn-primary.button-final'
    cancel_locator = By.CSS_SELECTOR, '.btn.btn-default.cancel'


@ui.register_ui(
    button_create_network=ui.Button(By.ID, 'networks__action_create'),
    button_delete_networks=ui.Button(By.ID, 'networks__action_delete'),
    form_add_subnet=FormAddSubnet(
        By.CSS_SELECTOR, 'form[action*="subnets/create"]'),
    form_create_network=FormCreateNetwork(
        By.CSS_SELECTOR, 'form[action*="networks/create"]'),
    table_networks=TableNetworks(By.ID, 'networks'))
class PageNetworks(PageBase):
    """Networks page."""

    url = "/project/networks/"
    navigate_items = 'Project', 'Network', 'Networks'
