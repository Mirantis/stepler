"""
----------------------------------------
Predefined UI components for page or tab
----------------------------------------
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

from stepler import config

from .form import Form


@ui.register_ui(
    item_exit=ui.UI(By.XPATH, "//a[@href='/auth/logout/']"),
    item_help=ui.Link(By.XPATH, "//a[@href='http://docs.openstack.org']"),
    item_download_rcv3=ui.UI(
        By.XPATH, "//a[@href='/project/api_access/openrc/']"),
    item_download_rcv2=ui.UI(
        By.XPATH, "//a[@href='/project/api_access/openrcv2/']"))
class DropdownMenuAccount(ui.Block):
    """Dropdown menu for account settings."""


@ui.register_ui(label_project=ui.UI(By.CSS_SELECTOR, '.context-project'))
class DropdownMenuProject(ui.Block):
    """Dropdown menu for project switching."""

    def item_project(self):
        """Get project item from from dropdown list."""
        return self.webelement.find_elements_by_xpath(
            '//ul[@class="dropdown-menu"]//li')[2]


class Spinner(ui.UI):
    """Spinner to wait loading."""

    timeout = config.ACTION_TIMEOUT


class Modal(ui.Block):
    """Spinner to wait loading."""

    timeout = config.ACTION_TIMEOUT


@ui.register_ui(
    dropdown_menu_account=DropdownMenuAccount(
        By.XPATH, '//span[@class="user-name"]'),
    dropdown_menu_project=DropdownMenuProject(
        By.XPATH, '//li[@class="dropdown"]/a'),
    form_confirm=Form(By.CSS_SELECTOR, 'div.modal-content > div.modal-footer'),
    modal=Modal(By.CLASS_NAME, 'modal_backdrop'),
    spinner=Spinner(By.CLASS_NAME, 'spinner'))
class InitiatedUI(ui.Container):
    """Predefined UI components for page or tab."""
