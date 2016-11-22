"""
---------------
Instances steps
---------------
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

from hamcrest import assert_that, equal_to, is_not  # noqa

from stepler.horizon import config
from stepler.third_party import steps_checker
from stepler.third_party import waiter

from .base import BaseSteps


class InstancesSteps(BaseSteps):
    """Instances steps."""

    def _page_instances(self):
        """Open instances page if it isn't opened."""
        return self._open(self.app.page_instances)

    @steps_checker.step
    def create_instance(self, instance_name, network_name='admin_internal_net',
                        count=1, check=True):
        """Step to create instance."""
        page_instances = self._page_instances()

        page_instances.button_launch_instance.click()
        with page_instances.form_launch_instance as form:

            with form.tab_details as tab:
                tab.field_name.value = instance_name
                tab.field_count.value = count

            form.item_source.click()
            with form.tab_source as tab:
                tab.combobox_boot_source.value = 'Image'
                tab.radio_volume_create.value = 'No'
                tab.table_available_sources.row(
                    name='TestVM').button_add.click()

            form.item_flavor.click()
            with form.tab_flavor as tab:
                tab.table_available_flavors.row(
                    name='m1.tiny').button_add.click()

            form.item_network.click()
            with form.tab_network as tab:
                if not tab.table_allocated_networks.row(
                        name=network_name).is_present:
                    tab.table_available_networks.row(
                        name=network_name).button_add.click()

            form.submit()

        instance_names = []
        for i in range(1, count + 1):
            if count == 1:
                instance_names.append(instance_name)
            else:
                instance_names.append('{}-{}'.format(instance_name, i))

        if check:
            for name in instance_names:
                page_instances.table_instances.row(
                    name=name).wait_for_status('Active')

        return instance_names

    @steps_checker.step
    def delete_instances(self, instance_names, check=True):
        """Step to delete instances."""
        page_instances = self._page_instances()

        for instance_name in instance_names:
            page_instances.table_instances.row(
                name=instance_name).checkbox.select()

        page_instances.button_delete_instances.click()
        page_instances.form_confirm.submit()

        if check:
            self.close_notification('success')
            for instance_name in instance_names:
                page_instances.table_instances.row(
                    name=instance_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def delete_instance(self, instance_name, check=True):
        """Step to delete instance."""
        page_instances = self._page_instances()

        with page_instances.table_instances.row(
                name=instance_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_instances.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_instances.table_instances.row(
                name=instance_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def lock_instance(self, instance_name, check=True):
        """Step to lock instance."""
        with self._page_instances().table_instances.row(
                name=instance_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_lock.click()

            if check:
                self.close_notification('success')

    @steps_checker.step
    def unlock_instance(self, instance_name, check=True):
        """Step to unlock instance."""
        with self._page_instances().table_instances.row(
                name=instance_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_unlock.click()

            if check:
                self.close_notification('success')

    @steps_checker.step
    def view_instance(self, instance_name, check=True):
        """Step to view instance."""
        self._page_instances().table_instances.row(
            name=instance_name).link_instance.click()

        if check:
            assert_that(self.app.page_instance.info_instance.label_name.value,
                        equal_to(instance_name))

    @steps_checker.step
    def filter_instances(self, query, check=True):
        """Step to filter instances."""
        page_instances = self._page_instances()

        page_instances.field_filter_instances.value = query
        page_instances.button_filter_instances.click()

        if check:
            def check_rows():
                for row in page_instances.table_instances.rows:
                    if not (row.is_present and
                            query in row.link_instance.value):
                        is_present = False
                        break
                is_present = True

                return waiter.expect_that(is_present, equal_to(True))

            waiter.wait(check_rows,
                        timeout_seconds=config.UI_TIMEOUT,
                        sleep_seconds=0.1)

    @steps_checker.step
    def reset_instances_filter(self, check=True):
        """Step to reset instances filter."""
        page_instances = self._page_instances()
        page_instances.field_filter_instances.value = ''
        page_instances.button_filter_instances.click()

        if check:
            assert_that(page_instances.field_filter_instances.value,
                        equal_to(''))

    @steps_checker.step
    def check_flavor_absent_in_instance_launch_form(self, flavor):
        """Step to check flavor is absent in instance launch form."""
        page_instances = self._page_instances()
        page_instances.button_launch_instance.click()

        with page_instances.form_launch_instance as form:
            form.item_flavor.click()

            waiter.wait(
                lambda: (form.tab_flavor.table_available_flavors.rows,
                         'No available flavors'),
                timeout_seconds=30,
                sleep_seconds=0.1)

            for row in form.tab_flavor.table_available_flavors.rows:
                assert_that(row.cell('name').value,
                            is_not(equal_to(flavor.name)))
            form.cancel()

    @steps_checker.step
    def check_instance_active(self, instance_name):
        """Step to check instance has active status."""
        self._page_instances().table_instances.row(
            name=instance_name).wait_for_status('Active')

    @steps_checker.step
    def check_instances_pagination(self, instances):
        """Step to check instances pagination."""
        page_instances = self._page_instances()
        page_instances.table_instances.row(
            name=instances[2].name).wait_for_presence(30)
        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_absence()

        page_instances.table_instances.link_next.click()

        page_instances.table_instances.row(
            name=instances[1].name).wait_for_presence(30)
        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_presence()

        page_instances.table_instances.link_next.click()

        page_instances.table_instances.row(
            name=instances[0].name).wait_for_presence(30)
        page_instances.table_instances.link_next.wait_for_absence()
        page_instances.table_instances.link_prev.wait_for_presence()

        page_instances.table_instances.link_prev.click()

        page_instances.table_instances.row(
            name=instances[1].name).wait_for_presence(30)
        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_presence()

        page_instances.table_instances.link_prev.click()

        page_instances.table_instances.row(
            name=instances[2].name).wait_for_presence(30)
        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_absence()
