"""
----------
Users page
----------
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
    item_change_password=ui.UI(By.CSS_SELECTOR,
                               '*[id*="action_change_password"]'),
    item_toggle_user=ui.UI(By.CSS_SELECTOR, '[id$="action_toggle"]'))
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for user row."""


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=DropdownMenu())
class RowUser(_ui.Row):
    """User row of users table."""


class TableUsers(_ui.Table):
    """Users table."""

    columns = {'name': 2, 'email': 4, 'enabled': 6}
    row_cls = RowUser


@ui.register_ui(
    field_name=ui.TextField(By.NAME, 'name'),
    field_password=ui.TextField(By.NAME, 'password'),
    field_confirm_password=ui.TextField(By.NAME, 'confirm_password'),
    combobox_project=_ui.combobox_by_label("Primary Project"),
    combobox_role=_ui.combobox_by_label('Role'))
class FormCreateUser(_ui.Form):
    """Form to create new user."""


@ui.register_ui(
    field_confirm_password=ui.TextField(By.NAME, 'confirm_password'),
    field_password=ui.TextField(By.NAME, 'password'))
class FormChangePassword(_ui.Form):
    """Form to change user password."""


@ui.register_ui(
    field_name=ui.TextField(By.NAME, 'name'))
class FormUpdateUser(_ui.Form):
    """Form to update user."""


@ui.register_ui(
    button_create_user=ui.Button(By.ID, 'users__action_create'),
    button_delete_users=ui.Button(By.ID, 'users__action_delete'),
    button_filter_users=ui.Button(By.XPATH, './/button[.="Filter"]'),
    field_filter_users=ui.TextField(By.NAME, 'users__filter__q'),
    form_change_password=FormChangePassword(By.ID,
                                            'change_user_password_form'),
    form_create_user=FormCreateUser(By.ID, 'create_user_form'),
    form_update_user=FormUpdateUser(By.ID, 'update_user_form'),
    table_users=TableUsers(By.ID, 'users'))
class PageUsers(PageBase):
    """Users page."""

    url = '/identity/users/'
    navigate_items = "Identity", "Users"
