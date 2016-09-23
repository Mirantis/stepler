"""
Horizon steps for authentication.

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

import pom

from .base import BaseSteps


class AccessSteps(BaseSteps):
    """Access & security steps."""

    def page_access(self):
        """Open access & security page."""
        return self._open(self.app.page_access)

    def tab_security_groups(self):
        """Open security groups tab."""
        with self.page_access() as page:
            page.label_security_groups.click()
            return page.tab_security_groups

    @pom.timeit('Step')
    def create_security_group(self, group_name, description=None, check=True):
        """Step to create security group."""
        tab_security_groups = self.tab_security_groups()
        tab_security_groups.button_create_security_group.click()

        with tab_security_groups.form_create_security_group as form:
            form.field_name.value = group_name

            if description:
                form.field_description.value = description

            form.submit()

        if check:
            self.close_notification('success')
            tab_security_groups.table_security_groups.row(
                name=group_name).wait_for_presence(30)

    @pom.timeit('Step')
    def delete_security_group(self, group_name, check=True):
        """Step to delete security group."""
        tab_security_groups = self.tab_security_groups()

        with tab_security_groups.table_security_groups.row(
                name=group_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        tab_security_groups.form_confirm.submit()

        if check:
            self.close_notification('success')
            tab_security_groups.table_security_groups.row(
                name=group_name).wait_for_absence()
