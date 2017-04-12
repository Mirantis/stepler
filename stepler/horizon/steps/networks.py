"""
--------------
Networks steps
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

import time

from hamcrest import assert_that, equal_to  # noqa

from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter


class NetworksSteps(base.BaseSteps):
    """networks steps."""

    def _page_networks(self):
        """Open networks page if it isn't opened."""
        return self._open(self.app.page_networks)

    def _page_admin_networks(self):
        """Open admin networks page if it isn't opened."""
        return self._open(self.app.page_admin_networks)

    @steps_checker.step
    def create_network(self,
                       network_name=None,
                       shared=False,
                       create_subnet=False,
                       subnet_name='subnet',
                       network_adress='192.168.0.0/24',
                       gateway_ip='192.168.0.1',
                       check=True):
        """Step to create network."""
        network_name = network_name or next(utils.generate_ids('network'))

        page_networks = self._page_networks()
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

        return network_name

    @steps_checker.step
    def delete_network(self, network_name, check=True):
        """Step to delete network."""
        page_networks = self._page_networks()

        with page_networks.table_networks.row(
                name=network_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_networks.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_networks.table_networks.row(
                name=network_name).wait_for_absence()

    @steps_checker.step
    def delete_networks(self, network_names, check=True):
        """Step to delete networks as batch."""
        page_networks = self._page_networks()

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

    @steps_checker.step
    def add_subnet(self, network_name, subnet_name=None,
                   network_address='10.109.3.0/24', check=True):
        """Step to add subnet for network."""
        subnet_name = subnet_name or next(utils.generate_ids('subnet'))

        page_networks = self._page_networks()

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
            page_network.open_tab_subnets().table_subnets.row(
                name=subnet_name,
                network_address=network_address).wait_for_presence()

        return subnet_name

    @steps_checker.step
    def admin_update_network(self, network_name, new_network_name=False,
                             shared=False, check=True):
        """Step to update network as admin."""
        page_networks = self._page_admin_networks()
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

    @steps_checker.step
    def admin_delete_network(self, network_name, check=True):
        """Step to delete network as admin."""
        page_networks = self._page_admin_networks()

        with page_networks.table_networks.row(
                name=network_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_networks.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_networks.table_networks.row(
                name=network_name).wait_for_absence()

    @steps_checker.step
    def admin_filter_networks(self, query, check=True):
        """Step to filter networks."""
        page_networks = self._page_admin_networks()

        page_networks.field_filter_networks.value = query
        page_networks.button_filter_networks.click()
        time.sleep(1)

        if check:

            def check_rows():
                for row in page_networks.table_networks.rows:
                    if not (row.is_present and
                            query in row.link_network.value):
                        is_present = False
                        break
                is_present = True

                return waiter.expect_that(is_present, equal_to(True))

            waiter.wait(check_rows,
                        timeout_seconds=10,
                        sleep_seconds=0.1)

    @steps_checker.step
    def check_network_present(self, network_name):
        """Step to check network is present."""
        self._page_networks().table_networks.row(
            name=network_name).wait_for_presence()

    @steps_checker.step
    def check_network_share_status(self, network_name, is_shared=True):
        """Step to check network share status."""
        share_status = 'Yes' if is_shared else 'No'
        with self._page_networks().table_networks.row(
                name=network_name).cell('shared') as cell:
            assert_that(cell.value, equal_to(share_status))
