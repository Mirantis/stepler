"""
Networks steps.

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
from waiting import wait

from .base import BaseSteps


class NetworksSteps(BaseSteps):
    """networks steps."""

    def page_networks(self):
        """Open networks page if it isn't opened."""
        return self._open(self.app.page_networks)

    def page_admin_networks(self):
        """Open admin networks page if it isn't opened."""
        return self._open(self.app.page_admin_networks)

    @pom.timeit('Step')
    def create_network(self, network_name, shared=False, create_subnet=False,
                       subnet_name='subnet', network_adress='192.168.0.0/24',
                       gateway_ip='192.168.0.1', check=True):
        """Step to create network."""
        page_networks = self.page_networks()
        page_networks.button_create_network.click()

        with page_networks.form_create_network as form:
            form.field_name.value = network_name

            if shared:
                form.checkbox_shared.select()
            else:
                form.checkbox_shared.unselect()

            if create_subnet:
                form.checkbox_create_subnet.select()
                form.button_next.click()

                form.field_subnet_name.value = subnet_name
                form.field_network_address.value = network_adress
                form.field_gateway_ip.value = gateway_ip

                form.button_next.click()
            else:
                form.checkbox_create_subnet.unselect()

            form.submit()

        if check:
            self.close_notification('success')
            page_networks.table_networks.row(
                name=network_name).wait_for_presence()

    @pom.timeit('Step')
    def delete_network(self, network_name, check=True):
        """Step to delete network."""
        page_networks = self.page_networks()

        with page_networks.table_networks.row(
                name=network_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_networks.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_networks.table_networks.row(
                name=network_name).wait_for_absence()

    @pom.timeit('Step')
    def delete_networks(self, network_names, check=True):
        """Step to delete networks as batch."""
        page_networks = self.page_networks()

        for network_name in network_names:
            page_networks.table_networks.row(
                name=network_name).checkbox.select()

        page_networks.button_delete_networks.click()
        page_networks.form_confirm.submit()

        if check:
            self.close_notification('success')
            for network_name in network_names:
                page_networks.table_networks.row(
                    name=network_name).wait_for_absence()

    @pom.timeit('Step')
    def add_subnet(self, network_name, subnet_name,
                   network_address='10.109.3.0/24', check=True):
        """Step to add subnet for network."""
        page_networks = self.page_networks()

        with page_networks.table_networks.row(
                name=network_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_add_subnet.click()

        with page_networks.form_add_subnet as form:
            form.field_name.value = subnet_name
            form.field_network_address.value = network_address
            form.button_next.click()
            form.submit()

        if check:
            page_network = self.app.page_network
            self.close_notification('success')
            page_network.table_subnets.row(
                name=subnet_name,
                network_address=network_address).wait_for_presence()

    @pom.timeit('Step')
    def admin_update_network(self, network_name, new_network_name=False,
                             shared=False, check=True):
        """Step to update network as admin."""
        page_networks = self.page_admin_networks()
        page_networks.table_networks.row(
            name=network_name).dropdown_menu.item_default.click()

        with page_networks.form_update_network as form:
            if new_network_name:
                form.field_name.value = new_network_name

            if shared:
                form.checkbox_shared.select()
            else:
                form.checkbox_shared.unselect()

            form.submit()

        if check:
            self.close_notification('success')
            page_networks.table_networks.row(
                name=new_network_name or network_name).wait_for_presence()

    @pom.timeit('Step')
    def admin_delete_network(self, network_name, check=True):
        """Step to delete network as admin."""
        page_networks = self.page_admin_networks()

        with page_networks.table_networks.row(
                name=network_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_networks.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_networks.table_networks.row(
                name=network_name).wait_for_absence()

    @pom.timeit('Step')
    def admin_filter_networks(self, query, check=True):
        """Step to filter networks."""
        page_networks = self.page_admin_networks()

        page_networks.field_filter_networks.value = query
        page_networks.button_filter_networks.click()
        pom.sleep(1, 'Wait table will be refreshed')

        if check:

            def check_rows():
                for row in page_networks.table_networks.rows:
                    if not (row.is_present and
                            query in row.link_network.value):
                        return False
                return True

            wait(check_rows, timeout_seconds=10, sleep_seconds=0.1)
