"""
Volume types tab.

@author: schipiga@mirantis.com
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


@ui.register_ui(
    field_description=ui.TextField(By.NAME, 'vol_type_description'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormCreateVolumeType(_ui.Form):
    """Form to create volume type."""


@ui.register_ui(dropdown_menu=_ui.DropdownMenu())
class RowVolumeType(_ui.Row):
    """Volume type row of volume types table."""


class TableVolumeTypes(_ui.Table):
    """Volume types table."""

    columns = {'name': 2}
    row_cls = RowVolumeType


@ui.register_ui(dropdown_menu=_ui.DropdownMenu())
class RowQosSpec(_ui.Row):
    """QoS Spec row of QoS Specs table."""


class TableQosSpecs(_ui.Table):
    """QoS Specs table."""

    columns = {'name': 2}
    row_cls = RowQosSpec


@ui.register_ui(
    field_consumer=ui.ComboBox(By.NAME, 'consumer'),
    field_name=ui.TextField(By.NAME, 'name'))
class FormCreateQosSpec(_ui.Form):
    """Form to create QoS Spec."""


@ui.register_ui(
    button_create_qos_spec=ui.Button(By.ID, 'qos_specs__action_create'),
    button_create_volume_type=ui.Button(By.ID, 'volume_types__action_create'),
    form_create_qos_spec=FormCreateQosSpec(
        By.CSS_SELECTOR, 'form[action*="volume_types/create_qos_spec"]'),
    form_create_volume_type=FormCreateVolumeType(
        By.CSS_SELECTOR, 'form[action*="volume_types/create_type"]'),
    table_qos_specs=TableQosSpecs(By.ID, 'qos_specs'),
    table_volume_types=TableVolumeTypes(By.ID, 'volume_types'))
class TabVolumeTypes(_ui.Tab):
    """Volume types tab."""
