"""
-----------------------------
Horizon steps security groups
-----------------------------
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

from hamcrest import assert_that, less_than  # noqa

from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils


class SecurityGroupsSteps(base.BaseSteps):
    """Security groups steps."""

    def _page_networks(self):
        """Open network page."""
        return self._open(self.app.page_networks)

    def _page_security_groups(self):
        """Open security groups page."""
        return self._open(self.app.page_security_groups)

    @steps_checker.step
    def create_security_group(self, group_name=None, description=None,
                              check=True):
        """Step to create security group."""
        group_name = group_name or next(utils.generate_ids('security-group'))

        page_security_groups = self._page_security_groups()
        page_security_groups.button_create_security_group.click()

        with page_security_groups.form_create_security_group as form:
            form.field_name.value = group_name

            if description:
                form.field_description.value = description

            form.submit()

        if check:
            self.close_notification('success')
            page_security_groups.table_security_groups.row(
                name=group_name).wait_for_presence(30)

        return group_name

    @steps_checker.step
    def delete_security_group(self, group_name, check=True):
        """Step to delete security group."""
        page_security_groups = self._page_security_groups()

        with page_security_groups.table_security_groups.row(
                name=group_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_security_groups.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_security_groups.table_security_groups.row(
                name=group_name).wait_for_absence()

    @steps_checker.step
    def add_group_rule(self, group_name, port_number='25', check=True):
        """Step to add rule to the security group."""
        with self._page_security_groups().table_security_groups.row(
                name=group_name).dropdown_menu as menu:
            menu.item_default.click()

        page_rules = self.app.page_manage_rules

        page_rules.button_add_rule.click()

        with page_rules.form_add_rule as form:
            form.field_port.value = port_number
            form.submit()

        if check:
            self.close_notification('success')
            page_rules.table_rules.row(
                port_range=port_number).wait_for_presence(30)

        return port_number

    @steps_checker.step
    def delete_group_rule(self, port_number, check=True):
        """Step to remove rule from the security group."""
        page_rules = self.app.page_manage_rules

        with page_rules.table_rules.row(port_range=port_number) as page:
            page.checkbox.click()
            page_rules.button_delete_rules.click()

        page_rules.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_rules.table_rules.row(
                port_range=port_number).wait_for_absence()
