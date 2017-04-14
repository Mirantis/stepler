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

from hamcrest import (assert_that, is_not, any_of,
                      equal_to_ignoring_case)  # noqa H301
import pom
from pom import ui
from selenium.webdriver.common.by import By

from stepler import config
from stepler.third_party import waiter


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
    def wait_for_status(self, status, timeout=config.EVENT_TIMEOUT):
        """Wait status value after transit statuses."""
        self.wait_for_presence()
        with self.cell('status') as cell:

            def _wait_cell_status():
                matchers = [equal_to_ignoring_case(status)
                            for status in self.transit_statuses]
                return waiter.expect_that(cell.value, is_not(
                    any_of(*matchers)))

            waiter.wait(_wait_cell_status, timeout_seconds=timeout)
            assert_that(cell.value, equal_to_ignoring_case(status))


@ui.register_ui(
    link_next=ui.UI(By.CSS_SELECTOR, 'a[href^="?marker="]'),
    link_prev=ui.UI(By.CSS_SELECTOR, 'a[href^="?prev_marker="]'),
    row_empty=ui.UI(By.CSS_SELECTOR, 'tr.empty'))
class Table(ui.Table):
    """Custom table."""

    row_cls = Row
    row_xpath = './/tr[not(contains(@class, "detail-row"))]'

    @property
    def rows(self):
        """Table rows."""
        rows = super(Table, self).rows
        if len(rows) == 1 and self.row_empty.is_present:
            return []
        else:
            return rows

    @property
    def columns(self):
        """Table columns {'name': position}."""
        _columns = {}
        for pos, cell in enumerate(self.header.cells, 1):
            column = cell.get_attribute('innerText').strip()
            if column:
                column = re.sub('[ -]', '_', column).lower()
                _columns[column] = pos
        return _columns
