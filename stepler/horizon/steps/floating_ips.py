"""
Floating IPs steps.

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


class FloatingIPsSteps(BaseSteps):
    """Floating IPs steps."""

    def tab_floating_ips(self):
        """Open floating IPs tab."""
        page_access = self._open(self.app.page_access)
        page_access.label_floating_ips.click()
        return page_access.tab_floating_ips

    @pom.timeit('Step')
    def allocate_floating_ip(self, check=True):
        """Step to allocate floating IP."""
        tab_floating_ips = self.tab_floating_ips()
        old_ips = self._current_floating_ips
        tab_floating_ips.button_allocate_ip.click()

        with tab_floating_ips.form_allocate_ip as form:
            form.submit()

        if check:
            self.close_notification('success')

            new_ips = self._current_floating_ips
            allocated_ip = new_ips - old_ips

            assert len(allocated_ip) == 1
            return allocated_ip.pop()

    @pom.timeit('Step')
    def release_floating_ip(self, ip, check=True):
        """Step to release floating IP."""
        tab_floating_ips = self.tab_floating_ips()

        with tab_floating_ips.table_floating_ips.row(
                ip_address=ip).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_release.click()

        tab_floating_ips.form_confirm.submit()

        if check:
            self.close_notification('success')
            tab_floating_ips.table_floating_ips.row(
                ip_address=ip).wait_for_absence()

    @pom.timeit('Step')
    def associate_floating_ip(self, ip, instance_name, check=True):
        """Step to associate floating IP."""
        tab_floating_ips = self.tab_floating_ips()
        tab_floating_ips.table_floating_ips.row(
            ip_address=ip).dropdown_menu.item_default.click()

        with tab_floating_ips.form_associate as form:
            form.combobox_port.value = instance_name
            form.submit()

        if check:
            self.close_notification('success')
            tab_floating_ips.table_floating_ips.row(
                ip_address=ip,
                mapped_fixed_ip_address=instance_name).wait_for_presence()

    @property
    def _current_floating_ips(self):
        ips = set()
        rows = self.app.page_access.tab_floating_ips.table_floating_ips.rows
        for row in rows:
            ip = row.cell('ip_address').value
            ips.add(ip)
        return ips
