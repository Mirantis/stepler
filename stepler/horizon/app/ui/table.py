"""
------------
Custom table
------------
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

import re

import pom
from pom import ui
from selenium.webdriver.common.by import By
from waiting import wait

from stepler.horizon.config import EVENT_TIMEOUT


class Cell(ui.Block):
    """Cell."""

    @property
    def value(self):
        """Cell value."""
        def _clean_html(raw_html):
            return re.sub(r'<.*?>', '', raw_html)

        return _clean_html(super(Cell, self).value).strip()


class Row(ui.Row):
    """Row."""

    cell_cls = Cell
    transit_statuses = ()

    @pom.timeit
    def wait_for_status(self, status, timeout=EVENT_TIMEOUT):
        """Wait status value after transit statuses."""
        self.wait_for_presence()
        with self.cell('status') as cell:
            wait(lambda: cell.value not in self.transit_statuses,
                 timeout_seconds=timeout, sleep_seconds=0.1)
            assert cell.value == status


@ui.register_ui(
    link_next=ui.UI(By.CSS_SELECTOR, 'a[href^="?marker="]'),
    link_prev=ui.UI(By.CSS_SELECTOR, 'a[href^="?prev_marker="]'),
    row_empty=ui.UI(By.CSS_SELECTOR, 'tr.empty'))
class Table(ui.Table):
    """Custom table."""

    row_cls = Row

    @property
    def rows(self):
        """Table rows."""
        rows = super(Table, self).rows
        if len(rows) == 1 and self.row_empty.is_present:
            return []
        else:
            return rows
