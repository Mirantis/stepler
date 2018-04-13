"""
-----------
Stacks page
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

from ..base import PageBase


@ui.register_ui(
    item_suspend_stack=ui.UI(By.CSS_SELECTOR, '*[id$="action_suspend"]'),
    item_resume_stack=ui.UI(By.CSS_SELECTOR, '*[id$="action_resume"]'),
    item_edit_stack=ui.UI(By.CSS_SELECTOR, '*[id$="action_edit"]'),
    item_delete_stack=ui.UI(By.CSS_SELECTOR, '*[id$="action_delete"]'))
class DropdownMenu(_ui.DropdownMenu):
    """Dropdown menu for stack row."""


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'),
    dropdown_menu=DropdownMenu(),
    link_stack=ui.Link(By.CSS_SELECTOR, 'td > hz-cell > hz-field > a'))
class RowStack(_ui.Row):
    """Row with stack in stacks table."""


class TableStacks(_ui.Table):
    """Stacks table."""
    columns = {'name': 2, 'status': 6}
    row_cls = RowStack


@ui.register_ui(
    combobox_template_source=_ui.combobox_by_label('Template Source'),
    combobox_env_source=_ui.combobox_by_label('Environment Source'),
    field_template_data=ui.TextField(By.NAME, 'template_data'),
    field_env_data=ui.TextField(By.NAME, 'environment_data'))
class FormCreateStack(_ui.Form):
    """Form to create stack."""


@ui.register_ui(
    field_name=ui.TextField(By.NAME, 'stack_name'),
    field_timeout=ui.TextField(By.NAME, 'timeout_mins'),
    field_admin_password=ui.TextField(By.NAME, 'password'),
    field_flavor=ui.TextField(By.NAME, '__param_flavor'),
    field_image=ui.TextField(By.NAME, '__param_image'),
    field_key=ui.TextField(By.NAME, '__param_key_name'),
    checkbox_rollback=_ui.CheckBox(By.NAME, 'enable_rollback'))
class FormLaunchStack(_ui.Form):
    """Form to lauch stack."""


class FormPreviewStack(_ui.Form):
    """Form to preview stack."""


class FormPreviewTemplate(_ui.Form):
    """Form to preview template."""


@ui.register_ui(
    button_create_stack=ui.Button(By.ID, 'stacks__action_launch'),
    button_preview_stack=ui.Button(By.ID, 'stacks__action_preview'),
    button_delete_stacks=ui.Button(By.ID, 'stacks__action_delete'),
    form_create_stack=FormCreateStack(By.CSS_SELECTOR,
                                      '[action*="/select_template"'),
    form_launch_stack=FormLaunchStack(By.CSS_SELECTOR,
                                      '[action*="/launch"'),
    form_preview_template=FormPreviewTemplate(
        By.CSS_SELECTOR, '[action*="/preview_template"]'),
    form_preview_stack=FormPreviewStack(By.CSS_SELECTOR,
                                        '[action*="/preview_template"'),
    table_stacks=TableStacks(By.ID, 'stacks'))
class PageStacks(PageBase):
    """Stacks page."""
    url = "/project/stacks/"
    navigate_items = 'Project', 'Orchestration', 'Stacks'
