"""
Volume page.

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

from ..base import PageBase


@ui.register_ui(
    field_name=ui.TextField(By.NAME, 'name'),
    field_transfer_id=ui.TextField(By.NAME, 'id'),
    field_transfer_key=ui.TextField(By.NAME, 'auth_key'))
class FormTransferInfo(_ui.Form):
    """Form with info about transfer."""


@ui.register_ui(form_transfer_info=FormTransferInfo(By.CSS_SELECTOR, 'form'))
class PageVolumeTransfer(PageBase):
    """Volume transfer info page."""

    url = "/project/volumes/{}/"
