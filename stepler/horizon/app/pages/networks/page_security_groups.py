"""
--------------------
Security groups page
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

from ..base import PageBase
from stepler.horizon.app import ui as _ui


@ui.register_ui(
    field_description=ui.TextField(By.NAME, 'description'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormCreateSecurityGroup(_ui.Form):
    """Form to create security group."""


@ui.register_ui(dropdown_menu=_ui.DropdownMenu())
class RowSecurityGroup(_ui.Row):
    """Security group row."""


class TableSecurityGroups(_ui.Table):
    """Security groups table."""

    row_cls = RowSecurityGroup


@ui.register_ui(
    button_create_security_group=ui.Button(
        By.ID, 'security_groups__action_create'),
    form_create_security_group=FormCreateSecurityGroup(
        By.ID, 'create_security_group_form'),
    table_security_groups=TableSecurityGroups(By.ID, 'security_groups'))
class PageSecurityGroups(PageBase):
    """Security groups page."""
    url = "/project/security_groups"
