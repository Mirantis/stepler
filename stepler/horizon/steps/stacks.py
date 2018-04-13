"""
------------
Stacks steps
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

from hamcrest import assert_that, equal_to, less_than  # noqa

from stepler import config
from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils


class StacksSteps(base.BaseSteps):
    """Stacks steps."""

    def _page_stacks(self):
        """Open stacks page if it isn't opened."""
        return self._open(self.app.page_stacks)

    @steps_checker.step
    def view_stack(self, stack, check=True):
        """Step to view stack."""
        page_stacks = self._page_stacks()
        stack_name = stack.stack_name

        page_stacks.table_stacks.row(
            name=stack_name).webdriver.find_element_by_partial_link_text(
                stack_name).click()

        self.app.page_stack.stack_info_main.wait_for_presence()

        if check:
            self.app.page_stack.table_resource_topology.is_present

    @steps_checker.step
    def check_stack(self, stack, check=True):
        """Step to check stack status."""
        page_stacks = self._page_stacks()
        stack_name = stack.stack_name

        with page_stacks.table_stacks.row(
                name=stack_name).dropdown_menu as menu:
            menu.item_default.click()

        if check:
            self.close_notification('success')
            page_stacks.table_stacks.row(
                name=stack_name).wait_for_status('Check Complete')
