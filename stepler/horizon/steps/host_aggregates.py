"""
---------------------
Host aggregates steps
---------------------
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

from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils


class HostAggregatesSteps(base.BaseSteps):
    """Host aggregates steps."""

    def _page_host_aggregates(self):
        """Open images page if it isn't opened."""
        return self._open(self.app.page_host_aggregates)

    @steps_checker.step
    def create_host_aggregate(self, host_aggregate_name=None, check=True):
        """Step to create host aggregate."""
        host_aggregate_name = (host_aggregate_name or
                               next(utils.generate_ids('host-aggregate')))

        page_host_aggregates = self._page_host_aggregates()
        page_host_aggregates.button_create_host_aggregate.click()

        with page_host_aggregates.form_create_host_aggregate as form:
            form.field_name.value = host_aggregate_name
            form.submit()

        if check:
            self.close_notification('success')
            page_host_aggregates.table_host_aggregates.row(
                name=host_aggregate_name).wait_for_presence()

        return host_aggregate_name

    @steps_checker.step
    def delete_host_aggregate(self, host_aggregate_name, check=True):
        """Step to delete host_aggregate."""
        page_host_aggregates = self._page_host_aggregates()

        with page_host_aggregates.table_host_aggregates.row(
                name=host_aggregate_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_host_aggregates.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_host_aggregates.table_host_aggregates.row(
                name=host_aggregate_name).wait_for_absence()

    @steps_checker.step
    def delete_host_aggregates(self, host_aggregate_names, check=True):
        """Step to delete host aggregates."""
        page_host_aggregates = self._page_host_aggregates()

        for host_aggregate_name in host_aggregate_names:
            page_host_aggregates.table_host_aggregates.row(
                name=host_aggregate_name).checkbox.select()

        page_host_aggregates.button_delete_host_aggregates.click()
        page_host_aggregates.form_confirm.submit()

        if check:
            self.close_notification('success')
            for host_aggregate_name in host_aggregate_names:
                page_host_aggregates.table_host_aggregates.row(
                    name=host_aggregate_name).wait_for_absence()
