"""
--------------
Overview steps
--------------
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

from hamcrest import assert_that, equal_to   # noqa H301

from stepler.horizon.steps import base
from stepler.third_party import steps_checker


class OverviewSteps(base.BaseSteps):
    """Overview steps."""

    def _page_overview(self):
        return self._open(self.app.page_overview)

    @steps_checker.step
    def get_used_resource_overview(self, resource_name):
        """Step to get used overview resources."""
        page_overview = self._page_overview()
        return page_overview.row_avaible_resource.value(resource_name)

    @steps_checker.step
    def check_resource_item_changed(self, resource_name,
                                    resource_before_creating, check=True):
        """Step to check that quantity of resource were grown."""
        page_overview = self._page_overview()
        resource_after_creating = page_overview.row_avaible_resource.value(
            resource_name)
        if check:
            assert_that(int(resource_after_creating), equal_to(
                int(resource_before_creating) + 1))
