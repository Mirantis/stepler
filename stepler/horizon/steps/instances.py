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

from hamcrest import (assert_that, contains_string, contains_inanyorder,
                      equal_to, greater_than, has_length, is_in, is_not)  # noqa

from stepler import config
from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter


class InstancesSteps(base.BaseSteps):
    """Instances steps."""

    def _page_instances(self):
        """Open instances page if it was not opened."""
        return self._open(self.app.page_instances)

    def _page_admin_instances(self):
        """Open admin instances page if it was not opened."""
        return self._open(self.app.page_admin_instances)

    def _get_current_instance_name(self, instance_names):
        """Getting current instance name."""
        rows = self._page_instances().table_instances.rows
        assert_that(rows, has_length(1))

        instance_name = rows[0].cell('name').value
        assert_that(instance_name, is_in(instance_names))

        return instance_name

    @steps_checker.step
    def create_instance(self, instance_name=None,
                        network_name='internal_net',
                        count=1,
                        check=True):
        """Step to create instance."""
        instance_name = instance_name or next(utils.generate_ids('instance'))

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
                    name=config.HORIZON_TEST_IMAGE_CIRROS).button_add.click()

            form.item_flavor.click()
            with form.tab_flavor as tab:
                tab.table_available_flavors.row(
                    name=config.HORIZON_TEST_FLAVOR_TINY).button_add.click()

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
        page_instances.form_submit.button_submit.click()

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

        page_instances.form_submit.button_submit.click()

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
        page_instances.button_instance_filter().click()
        page_instances.item_instance_parameter(config.INSTANCE_NAME).click()
        page_instances.field_filter_instances.value = query
        page_instances.button_filter_instances.click()

        if check:
            def check_rows():
                is_present = False
                for row in page_instances.table_instances.rows:
                    if not (row.is_present and
                            query in row.link_instance.value):
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
    def check_instances_sum(self, instance_names, min_instances_sum=2):
        """Step to check quantity of instances."""
        assert_that(instance_names,
                    has_length(greater_than(min_instances_sum)))

    @steps_checker.step
    def check_instances_pagination(self, instance_names):
        """Step to check instances pagination."""

        ordered_names = []
        count = len(instance_names)
        page_instances = self._page_instances()

        # instances can be unordered so we should try to retrieve
        # any instance from instances list

        instance_name = self._get_current_instance_name(instance_names)
        ordered_names.append(instance_name)
        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_absence()

        # check all elements except the first one and the last one
        for _ in range(1, count - 1):
            page_instances.table_instances.link_next.click()

            instance_name = self._get_current_instance_name(instance_names)
            ordered_names.append(instance_name)
            page_instances.table_instances.link_next.wait_for_presence()
            page_instances.table_instances.link_prev.wait_for_presence()

        page_instances.table_instances.link_next.click()

        instance_name = self._get_current_instance_name(instance_names)
        ordered_names.append(instance_name)
        page_instances.table_instances.link_next.wait_for_absence()
        page_instances.table_instances.link_prev.wait_for_presence()

        # check that all created instance names have been checked
        assert_that(ordered_names, contains_inanyorder(*instance_names))

        for i in range(count - 2, 0, -1):
            page_instances.table_instances.link_prev.click()

            page_instances.table_instances.row(
                name=ordered_names[i]).wait_for_presence(30)
            page_instances.table_instances.link_next.wait_for_presence()
            page_instances.table_instances.link_prev.wait_for_presence()

        page_instances.table_instances.link_prev.click()

        page_instances.table_instances.row(
            name=ordered_names[0]).wait_for_presence(30)
        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_absence()

    @steps_checker.step
    def check_admin_instances_pagination(self, instance_names):
        """Step to check instances pagination as admin."""

        ordered_names = []
        count = len(instance_names)
        page_instances = self._page_admin_instances()

        # instances can be unordered so we should try to retrieve
        # any instance from instances list

        instance_name = self._get_current_instance_name(instance_names)
        ordered_names.append(instance_name)

        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_absence()

        # check all elements except the first one and the last one
        for _ in range(1, count - 1):
            page_instances.table_instances.link_next.click()

            instance_name = self._get_current_instance_name(instance_names)
            ordered_names.append(instance_name)
            page_instances.table_instances.link_next.wait_for_presence()
            page_instances.table_instances.link_prev.wait_for_presence()

        page_instances.table_instances.link_next.click()

        instance_name = self._get_current_instance_name(instance_names)
        ordered_names.append(instance_name)
        page_instances.table_instances.link_next.wait_for_absence()
        page_instances.table_instances.link_prev.wait_for_presence()

        # check that all created instance names have been checked
        assert_that(ordered_names, contains_inanyorder(*instance_names))

        for i in range(count - 2, 0, -1):
            page_instances.table_instances.link_prev.click()

            page_instances.table_instances.row(
                name=ordered_names[i]).wait_for_presence(30)
            page_instances.table_instances.link_next.wait_for_presence()
            page_instances.table_instances.link_prev.wait_for_presence()

        page_instances.table_instances.link_prev.click()

        page_instances.table_instances.row(
            name=ordered_names[0]).wait_for_presence(30)
        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_absence()

    @steps_checker.step
    def nova_associate_floating_ip(self, instance_name, ip, check=True):
        """Step to associate floating IP."""
        page_instances = self._page_instances()
        with page_instances.table_instances.row(
                name=instance_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_associate.click()

        with page_instances.form_associate_floating_ip as form:
            form.combobox_float_ip.value = ip
            form.submit()

        if check:
            self.close_notification('success')

    @steps_checker.step
    def nova_disassociate_floating_ip(self, instance_name, check=True):
        """Step to disassociate floating IP."""
        page_instances = self._page_instances()
        with page_instances.table_instances.row(
                name=instance_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_disassociate.click()

        page_instances.form_submit.button_submit.click()

        if check:
            self.close_notification('success')

    @steps_checker.step
    def create_instance_snapshot(self, instance_name,
                                 snapshot_name=None,
                                 check=True):
        """Step to create instance snapshot."""
        snapshot_name = snapshot_name or next(
            utils.generate_ids('snapshot'))
        self._page_instances().table_instances.row(
            name=instance_name).dropdown_menu.click()

        with self._page_instances().form_create_instance_snapshot as form:
            form.item_snapshot_name.value = snapshot_name
            form.submit()

        if check:
            self.close_notification('success')
        return snapshot_name

    @steps_checker.step
    def resize_instance(self, instance_name,
                        flavor=None, check=True):
        """Step to resize instance."""
        page_instances = self._page_instances()
        flavor = flavor or config.FLAVOR_TINY
        with page_instances.table_instances.row(
                name=instance_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_resize.click()
        with page_instances.form_resize_instance as form:
            form.wait_for_presence()
            form.item_flavor.value = flavor
            form.submit()

        with page_instances.table_instances.row(name=instance_name) as row:

            def _poll_instance_status():
                return row.cell('status').value == config.CONFIM_RESIZE_STATUS

        waiter.wait(lambda: _poll_instance_status(),
                    timeout_seconds=config.VERIFY_RESIZE_TIMEOUT,
                    sleep_seconds=config.VERIFY_RESIZE_SLEEP) is True
        page_instances.table_instances.row(
            name=instance_name).dropdown_menu.item_default.click()

        if check:
            row = page_instances.table_instances.row(
                name=instance_name)
            assert_that(row.cell('size').value,
                        contains_string(flavor))

    @steps_checker.step
    def rename_instance(self,
                        instance_name,
                        new_instance_name=None, check=True):
        """Step to rename instance."""
        new_instance_name = new_instance_name or next(utils.generate_ids(
            'instance'))
        page_instances = self._page_instances()
        with page_instances.table_instances.row(
                name=instance_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_edit_instance.click()
        with page_instances.form_edit_instance as form:
            form.item_instance_name.value = new_instance_name
            form.submit()

        if check:
            page_instances.table_instances.row(
                name=new_instance_name).wait_for_presence()
        return new_instance_name

    @steps_checker.step
    def admin_filter_instances(self, query, check=True):
        """Step to filter instances as admin."""
        page_instances = self._page_admin_instances()

        page_instances.item_instance_parameter(config.INSTANCE_NAME).click()
        page_instances.field_filter_instances.value = query
        page_instances.button_filter_instances.click()

        if check:
            def check_rows():
                is_present = False
                for row in page_instances.table_instances.rows:
                    if not (row.is_present and
                            query in row.link_instance.value):
                        break
                    is_present = True

                return waiter.expect_that(is_present, equal_to(True))

            waiter.wait(check_rows,
                        timeout_seconds=config.UI_TIMEOUT,
                        sleep_seconds=0.1)

    @steps_checker.step
    def admin_reset_instances_filter(self, check=True):
        """Step to reset instances filter as admin."""
        page_instances = self._page_admin_instances()
        page_instances.field_filter_instances.value = ''
        page_instances.button_filter_instances.click()

        if check:
            assert_that(page_instances.field_filter_instances.value,
                        equal_to(''))

    @steps_checker.step
    def add_security_group(self,
                           instance_name,
                           security_group_name,
                           check=True):
        """Step to add security group."""
        page_instances = self._page_instances()
        with page_instances.table_instances.row(
                name=instance_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_edit_instance.click()

        with page_instances.form_edit_instance as form:
            form.item_security_groups.click()
            form.item_security_group(security_group_name).click()
            form.submit()

        if check:
            self.close_notification('success')

    @steps_checker.step
    def check_instances_pagination_filter(self, instance_names):
        """Step to check instances pagination with filtering."""

        page_instances = self._page_instances()
        instance_name = self._get_current_instance_name(instance_names)

        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_absence()

        page_instances.table_instances.link_next.click()
        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_presence()

        page_instances.field_filter_instances.value = instance_name
        page_instances.button_filter_instances.click()

        def check_rows():
            is_present = False
            for row in page_instances.table_instances.rows:
                if not (row.is_present and
                        instance_name in row.link_instance.value):
                    break
                is_present = True

            return waiter.expect_that(is_present, equal_to(True))

        waiter.wait(check_rows,
                    timeout_seconds=config.UI_TIMEOUT,
                    sleep_seconds=0.1)

    @steps_checker.step
    def check_admin_instances_pagination_filter(self, instance_names):
        """Step to check instances pagination with filtering as admin."""

        instance_name = self._get_current_instance_name(instance_names)
        page_instances = self._page_admin_instances()

        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_absence()

        page_instances.table_instances.link_next.click()
        page_instances.table_instances.link_next.wait_for_presence()
        page_instances.table_instances.link_prev.wait_for_presence()

        page_instances.item_instance_parameter(config.INSTANCE_NAME).click()
        page_instances.field_filter_instances.value = instance_name
        page_instances.button_filter_instances.click()

        def check_rows():
            is_present = False
            for row in page_instances.table_instances.rows:
                if not (row.is_present and
                        instance_name in row.link_instance.value):
                    break
                is_present = True

            return waiter.expect_that(is_present, equal_to(True))

        waiter.wait(check_rows,
                    timeout_seconds=config.UI_TIMEOUT,
                    sleep_seconds=0.1)

    @steps_checker.step
    def admin_delete_instance(self, instance_name, check=True):
        """Step to delete instance as admin."""
        page_instances = self._page_admin_instances()

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
    def admin_delete_instances(self, instance_names, check=True):
        """Step to delete instances as admin."""
        page_instances = self._page_admin_instances()

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
    def check_instance_suspend(self, instance_name):
        """Step to check that instance was suspended."""
        page_instances = self._page_instances()
        with page_instances.table_instances.row(
                name=instance_name).dropdown_menu as menu:
                menu.button_toggle.click()
                menu.item_suspend.click()

        with page_instances.table_instances.row(
                name=instance_name) as row:
                row.transit_statuses += ('Active',)
                row.wait_for_status('Suspended')

    @steps_checker.step
    def check_instance_pause(self, instance_name):
        """Step to check that instance was paused."""
        page_instances = self._page_instances()
        with page_instances.table_instances.row(
                name=instance_name).dropdown_menu as menu:
                menu.button_toggle.click()
                menu.item_pause.click()

        with page_instances.table_instances.row(
                name=instance_name) as row:
                row.transit_statuses += ('Active',)
                row.wait_for_status('Paused')
