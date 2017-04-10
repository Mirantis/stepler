"""
-------------
Volumes steps
-------------
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

from hamcrest import (any_of, assert_that, contains_inanyorder, equal_to,
                      greater_than, has_length, is_in,
                      starts_with)   # noqa H301

from stepler import config
from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter


class VolumesSteps(base.BaseSteps):
    """Volumes steps."""

    def _page_volumes(self):
        """Open volumes page if it isn't opened."""
        return self._open(self.app.page_volumes)

    def _tab_volumes(self):
        """Open volumes tab."""
        with self._page_volumes() as page:
            page.label_volumes.click()
            return page.tab_volumes

    @steps_checker.step
    def create_volume(self, volume_name=None,
                      source_type=config.IMAGE_SOURCE,
                      source_name=None,
                      volume_type=None,
                      volume_size=None,
                      description=None,
                      check=True):
        """Step to create volume.

        Args:
            volume_name (str): name of volume
            source_type (str): type of source. Should be one of
                "Image" or "Volume"
            source_name (str): name of source (image or volume) to
                create volume from it
            volume_type (str): type of volume
            volume_size (int): Size of volume in GB
            description (str): description of volume
            check (bool): flag whether to check step or not

        Returns:
            str: name of created volume

        Raises:
            AssertionError: if check failed
        """
        assert_that(source_type,
                    any_of(config.IMAGE_SOURCE, config.VOLUME_SOURCE),
                    'source_type should be one of {}'.format(
                        [config.IMAGE_SOURCE, config.VOLUME_SOURCE]))

        volume_name = volume_name or next(utils.generate_ids('volume'))

        tab_volumes = self._tab_volumes()
        tab_volumes.button_create_volume.click()

        with tab_volumes.form_create_volume as form:
            form.field_name.value = volume_name
            form.combobox_source_type.value = source_type

            if source_type == config.IMAGE_SOURCE:

                image_sources = form.combobox_image_source.values
                image_source = source_name or image_sources[-1]

                form.combobox_image_source.value = image_source

            else:
                volume_sources = form.combobox_volume_source.values
                volume_source = source_name or volume_sources[-1]

                form.combobox_volume_source.value = volume_source

            if volume_type is not None:
                if not volume_type:
                    volume_type = form.combobox_volume_type.values[-1]
                form.combobox_volume_type.value = volume_type

            if volume_size is not None:
                form.field_size.value = volume_size

            if description is not None:
                form.field_description.value = description

            form.submit()

        if check:
            self.close_notification('info')
            row = tab_volumes.table_volumes.row(name=volume_name)
            row.wait_for_status('Available')
            if description is not None:
                assert_that(row.cell('description').value,
                            starts_with(description[:30]))

        return volume_name

    @steps_checker.step
    def delete_volume(self, volume_name, check=True):
        """Step to delete volume."""
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        tab_volumes.form_confirm.submit()

        if check:
            self.close_notification('success')
            tab_volumes.table_volumes.row(
                name=volume_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def edit_volume(self, volume_name, new_volume_name, check=True):
        """Step to edit volume."""
        tab_volumes = self._tab_volumes()

        tab_volumes.table_volumes.row(
            name=volume_name).dropdown_menu.item_default.click()

        tab_volumes.form_edit_volume.field_name.value = new_volume_name
        tab_volumes.form_edit_volume.submit()

        if check:
            self.close_notification('info')
            tab_volumes.table_volumes.row(
                name=new_volume_name).wait_for_presence()

    @steps_checker.step
    def delete_volumes(self, volume_names, check=True):
        """Step to delete volumes."""
        tab_volumes = self._tab_volumes()

        for volume_name in volume_names:
            tab_volumes.table_volumes.row(
                name=volume_name).checkbox.select()

        tab_volumes.button_delete_volumes.click()
        tab_volumes.form_confirm.submit()

        if check:
            self.close_notification('success')
            for volume_name in volume_names:
                tab_volumes.table_volumes.row(
                    name=volume_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def view_volume(self, volume_name, check=True):
        """Step to view volume."""
        self._tab_volumes().table_volumes.row(
            name=volume_name).link_volume.click()

        if check:
            assert_that(self.app.page_volume.info_volume.label_name.value,
                        equal_to(volume_name))

    @steps_checker.step
    def change_volume_type(self, volume_name, volume_type=None, check=True):
        """Step to change volume type."""
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_change_volume_type.click()

        with tab_volumes.form_change_volume_type as form:
            if not volume_type:
                volume_type = form.combobox_volume_type.values[-1]
            form.combobox_volume_type.value = volume_type
            form.submit()

        if check:
            self.close_notification('info')
            tab_volumes.table_volumes.row(
                name=volume_name, type=volume_type).wait_for_presence()

    @steps_checker.step
    def upload_volume_to_image(self, volume_name, image_name, check=True):
        """Step to upload volume to image."""
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_upload_to_image.click()

        with tab_volumes.form_upload_to_image as form:
            form.field_image_name.value = image_name
            form.submit()

        if check:
            self.close_notification('info')
            tab_volumes.table_volumes.row(
                name=volume_name).wait_for_status('Available')

    @steps_checker.step
    def extend_volume(self, volume_name, new_size=2, check=True):
        """Step to extend volume size."""
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_extend_volume.click()

        with tab_volumes.form_extend_volume as form:
            form.field_new_size.value = new_size
            form.submit()

        if check:
            self.close_notification('info')
            tab_volumes.table_volumes.row(
                name=volume_name, size=new_size).wait_for_presence()

    def _page_admin_volumes(self):
        """Open admin volumes page if it isn't opened."""
        return self._open(self.app.page_admin_volumes)

    def _tab_admin_volumes(self):
        """Open admin volumes tab."""
        with self._page_admin_volumes() as page:
            page.label_volumes.click()
            return page.tab_volumes

    @steps_checker.step
    def change_volume_status(self, volume_name, status=None, check=True):
        """Step to change volume status."""
        tab_volumes = self._tab_admin_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_update_volume_status.click()

        with tab_volumes.form_update_volume_status as form:
            if not status:
                status = form.combobox_status.values[-1]
            form.combobox_status.value = status
            form.submit()

        if check:
            self.close_notification('success')
            tab_volumes.table_volumes.row(
                name=volume_name, status=status).wait_for_presence()

    @steps_checker.step
    def launch_volume_as_instance(self, volume_name, instance_name,
                                  network_name, count=1, check=True):
        """Step to launch volume as instance."""
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_launch_volume_as_instance.click()

        with tab_volumes.form_launch_instance as form:

            with form.tab_details as tab:
                tab.field_name.value = instance_name
                tab.field_count.value = count

            form.item_flavor.click()
            with form.tab_flavor as tab:
                tab.table_available_flavors.row(
                    name=config.HORIZON_TEST_FLAVOR).button_add.click()

            form.item_network.click()
            with form.tab_network as tab:
                if not tab.table_allocated_networks.row(
                        name=network_name).is_present:
                    tab.table_available_networks.row(
                        name=network_name).button_add.click()

            form.submit()

            if check:
                form.wait_for_absence()

    @steps_checker.step
    def attach_instance(self, volume_name, instance_name, check=True):
        """Step to attach instance."""
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_manage_attachments.click()

        with tab_volumes.form_manage_attachments as form:
            instance_value = next(val for val in form.combobox_instance.values
                                  if instance_name in val)
            form.combobox_instance.value = instance_value
            form.submit()

        if check:
            self.close_notification('info')

            with tab_volumes.table_volumes.row(name=volume_name) as row:
                row.wait_for_status('In-use')
                assert instance_name in row.cell('attached_to').value

    @steps_checker.step
    def detach_instance(self, volume_name, instance_name, check=True):
        """Step to detach instance."""
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_manage_attachments.click()

        tab_volumes.form_manage_attachments.table_instances.row(
            name=instance_name).detach_volume_button.click()

        tab_volumes.form_confirm.submit()

        if check:
            self.close_notification('success')
            tab_volumes.table_volumes.row(
                name=volume_name).wait_for_status('Available')

    @steps_checker.step
    def create_transfer(self, volume_name, transfer_name, check=True):
        """Step to create transfer."""
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_create_transfer.click()

        with tab_volumes.form_create_transfer as form:
            form.field_name.value = transfer_name
            form.submit()

        if check:
            self.close_notification('success')

            with self.app.page_volume_transfer.form_transfer_info as form:
                transfer_id = form.field_transfer_id.value
                transfer_key = form.field_transfer_key.value

            self._tab_admin_volumes().table_volumes.row(
                name=volume_name,
                status='awaiting-transfer').wait_for_presence()

        return transfer_id, transfer_key

    @steps_checker.step
    def accept_transfer(self, transfer_id, transfer_key, volume_name,
                        check=True):
        """Step to accept transfer."""
        tab_volumes = self._tab_volumes()

        tab_volumes.button_accept_transfer.click()

        with tab_volumes.form_accept_transfer as form:
            form.field_transfer_id.value = transfer_id
            form.field_transfer_key.value = transfer_key
            form.submit()

        if check:
            self.close_notification('success')
            tab_volumes.table_volumes.row(
                name=volume_name, status='Available').wait_for_presence()

    @steps_checker.step
    def migrate_volume(self, volume_name, new_host=None, check=True):
        """Step to migrate host."""
        tab_volumes = self._tab_admin_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_migrate_volume.click()

        with tab_volumes.form_migrate_volume as form:
            old_host = form.field_current_host.value

            if not new_host:
                new_host = form.combobox_destination_host.values[-1]

            form.combobox_destination_host.value = new_host
            form.submit()

        if check:
            self.close_notification('success')

            tab_volumes.table_volumes.row(
                name=volume_name, host=new_host,
                status='Available').wait_for_presence()

            page_volumes = self._page_admin_volumes()

            def is_old_host_volume_absent():
                page_volumes.refresh()
                page_volumes.label_volumes.click()
                return waiter.expect_that(
                    page_volumes.tab_volumes.table_volumes.row(
                        name=volume_name, host=old_host).is_present,
                    equal_to(False))

            waiter.wait(is_old_host_volume_absent,
                        timeout_seconds=config.EVENT_TIMEOUT * 2)

        return old_host, new_host

    def _tab_snapshots(self):
        """Open volume snapshots tab."""
        with self._page_volumes() as page:
            page.label_snapshots.click()
            return page.tab_snapshots

    def _tab_backups(self):
        """Open volume backups tab."""
        with self._page_volumes() as page:
            page.label_backups.click()
            return page.tab_backups

    @steps_checker.step
    def create_snapshot(self, volume_name, snapshot_name=None,
                        description=None, check=True):
        """Step to create volume snapshot."""
        snapshot_name = snapshot_name or next(utils.generate_ids('snapshot'))

        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_create_snapshot.click()

        with tab_volumes.form_create_snapshot as form:
            form.field_name.value = snapshot_name
            if description is not None:
                form.field_description.value = description
            form.submit()

        if check:
            self.close_notification('info')
            row = self._tab_snapshots().table_snapshots.row(name=snapshot_name)
            row.wait_for_status('Available',
                                timeout=config.EVENT_TIMEOUT * 2)
            if description is not None:
                assert_that(row.cell('description').value,
                            starts_with(description[:30]))

        return snapshot_name

    @steps_checker.step
    def delete_snapshot(self, snapshot_name, check=True):
        """Step to delete volume snapshot."""
        tab_snapshots = self._tab_snapshots()

        with tab_snapshots.table_snapshots.row(
                name=snapshot_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        tab_snapshots.form_confirm.submit()

        if check:
            self.close_notification('success')
            tab_snapshots.table_snapshots.row(
                name=snapshot_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def delete_snapshots(self, snapshot_names, check=True):
        """Step to delete volume snapshots."""
        tab_snapshots = self._tab_snapshots()

        for snapshot_name in snapshot_names:
            tab_snapshots.table_snapshots.row(
                name=snapshot_name).checkbox.select()

        tab_snapshots.button_delete_snapshots.click()
        tab_snapshots.form_confirm.submit()

        if check:
            self.close_notification('success')
            for snapshot_name in snapshot_names:
                tab_snapshots.table_snapshots.row(
                    name=snapshot_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def update_snapshot(self, snapshot_name, new_snapshot_name,
                        description=None, check=True):
        """Step to update volume snapshot."""
        tab_snapshots = self._tab_snapshots()

        with tab_snapshots.table_snapshots.row(
                name=snapshot_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_edit.click()

        with tab_snapshots.form_edit_snapshot as form:
            form.field_name.value = new_snapshot_name
            if description is not None:
                form.field_description.value = description
            form.submit()

        if check:
            self.close_notification('info')
            self._tab_snapshots().table_snapshots.row(
                name=new_snapshot_name,
                status='Available').wait_for_presence()

    @steps_checker.step
    def create_volume_from_snapshot(self, snapshot_name, check=True):
        """Step to create volume from spanshot."""
        tab_snapshots = self._tab_snapshots()

        with tab_snapshots.table_snapshots.row(
                name=snapshot_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_default.click()

        tab_snapshots.form_create_volume.submit()

        if check:
            self.close_notification('info')
            self._tab_volumes().table_volumes.row(
                name=snapshot_name).wait_for_status('Available')

    @steps_checker.step
    def create_backup(self, volume_name, backup_name=None, description=None,
                      container=None, check=True):
        """Step to create volume backup."""
        backup_name = backup_name or next(utils.generate_ids('backup'))

        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_create_backup.click()

        with tab_volumes.form_create_backup as form:
            form.field_name.value = backup_name

            if description is not None:
                form.field_description.value = description

            if container is not None:
                form.field_container.value = container

            form.submit()

        if check:
            self.close_notification('info')
            row = self._tab_backups().table_backups.row(name=backup_name)
            row.wait_for_status(status='Available')
            if description is not None:
                assert_that(row.cell('description').value,
                            starts_with(description[:30]))

        return backup_name

    @steps_checker.step
    def delete_backups(self, backup_names, check=True):
        """Step to delete volume backups."""
        tab_backups = self._tab_backups()

        for backup_name in backup_names:
            tab_backups.table_backups.row(
                name=backup_name).checkbox.select()

        tab_backups.button_delete_backups.click()
        tab_backups.form_confirm.submit()

        if check:
            self.close_notification('success')
            for backup_name in backup_names:
                tab_backups.table_backups.row(
                    name=backup_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def check_volume_present(self, volume_name, timeout=None):
        """Check volume is present."""
        self._tab_volumes().table_volumes.row(
            name=volume_name, status='Available').wait_for_presence(timeout)

    @steps_checker.step
    def check_volumes_pagination(self, volume_names):
        """Step to check volumes pagination."""
        assert_that(volume_names, has_length(greater_than(2)))

        ordered_names = []
        count = len(volume_names)
        tab_volumes = self._tab_volumes()

        # volume names can be unordered so we should try to retrieve
        # any volume from volume_names list
        def _get_current_volume_name():
            rows = tab_volumes.table_volumes.rows
            assert_that(rows, has_length(1))

            volume_name = rows[0].cell('name').value
            assert_that(volume_name, is_in(volume_names))

            return volume_name

        volume_name = _get_current_volume_name()
        ordered_names.append(volume_name)

        assert_that(tab_volumes.table_volumes.link_next.is_present,
                    equal_to(True))
        assert_that(tab_volumes.table_volumes.link_prev.is_present,
                    equal_to(False))

        # check all elements except for the first and the last
        for _ in range(1, count - 1):
            tab_volumes.table_volumes.link_next.click()
            volume_name = _get_current_volume_name()
            ordered_names.append(volume_name)

            assert_that(tab_volumes.table_volumes.link_next.is_present,
                        equal_to(True))
            assert_that(tab_volumes.table_volumes.link_prev.is_present,
                        equal_to(True))

        tab_volumes.table_volumes.link_next.click()
        volume_name = _get_current_volume_name()
        ordered_names.append(volume_name)

        assert_that(tab_volumes.table_volumes.link_next.is_present,
                    equal_to(False))
        assert_that(tab_volumes.table_volumes.link_prev.is_present,
                    equal_to(True))

        # check that all created volume names have been checked
        assert_that(ordered_names, contains_inanyorder(*volume_names))

        # check all elements except for the first and the last
        for i in range(count - 2, 0, -1):
            tab_volumes.table_volumes.link_prev.click()
            tab_volumes.table_volumes.row(
                name=ordered_names[i]).wait_for_presence(30)

            assert_that(tab_volumes.table_volumes.link_next.is_present,
                        equal_to(True))
            assert_that(tab_volumes.table_volumes.link_prev.is_present,
                        equal_to(True))

        tab_volumes.table_volumes.link_prev.click()
        tab_volumes.table_volumes.row(
            name=ordered_names[0]).wait_for_presence(30)

        assert_that(tab_volumes.table_volumes.link_next.is_present,
                    equal_to(True))
        assert_that(tab_volumes.table_volumes.link_prev.is_present,
                    equal_to(False))

    @steps_checker.step
    def check_snapshots_pagination(self, snapshot_names):
        """Step to check snapshots pagination."""
        assert_that(snapshot_names, has_length(greater_than(2)))

        ordered_names = []
        count = len(snapshot_names)
        tab_snapshots = self._tab_snapshots()

        # snapshot names can be unordered so we should try to retrieve
        # any snapshot from snapshot_names list
        def _get_current_snapshot_name():
            rows = tab_snapshots.table_snapshots.rows
            assert_that(rows, has_length(1))

            snapshot_name = rows[0].cell('name').value
            assert_that(snapshot_name, is_in(snapshot_names))

            return snapshot_name

        snapshot_name = _get_current_snapshot_name()
        ordered_names.append(snapshot_name)

        assert_that(tab_snapshots.table_snapshots.link_next.is_present,
                    equal_to(True))
        assert_that(tab_snapshots.table_snapshots.link_prev.is_present,
                    equal_to(False))

        # check all elements except for the first and the last
        for _ in range(1, count - 1):
            tab_snapshots.table_snapshots.link_next.click()
            snapshot_name = _get_current_snapshot_name()
            ordered_names.append(snapshot_name)

            assert_that(tab_snapshots.table_snapshots.link_next.is_present,
                        equal_to(True))
            assert_that(tab_snapshots.table_snapshots.link_prev.is_present,
                        equal_to(True))

        tab_snapshots.table_snapshots.link_next.click()
        snapshot_name = _get_current_snapshot_name()
        ordered_names.append(snapshot_name)

        assert_that(tab_snapshots.table_snapshots.link_next.is_present,
                    equal_to(False))
        assert_that(tab_snapshots.table_snapshots.link_prev.is_present,
                    equal_to(True))

        # check that all created volume names have been checked
        assert_that(ordered_names, contains_inanyorder(*snapshot_names))

        for i in range(count - 2, 0, -1):
            tab_snapshots.table_snapshots.link_prev.click()
            tab_snapshots.table_snapshots.row(
                name=ordered_names[i]).wait_for_presence(30)

            assert_that(tab_snapshots.table_snapshots.link_next.is_present,
                        equal_to(True))
            assert_that(tab_snapshots.table_snapshots.link_prev.is_present,
                        equal_to(True))

        tab_snapshots.table_snapshots.link_prev.click()
        tab_snapshots.table_snapshots.row(
            name=ordered_names[0]).wait_for_presence(30)

        assert_that(tab_snapshots.table_snapshots.link_next.is_present,
                    equal_to(True))
        assert_that(tab_snapshots.table_snapshots.link_prev.is_present,
                    equal_to(False))

    @steps_checker.step
    def check_backups_pagination(self, backup_names):
        """Step to check backups pagination."""
        assert_that(backup_names, has_length(greater_than(2)))

        ordered_names = []
        count = len(backup_names)
        tab_backups = self._tab_backups()

        # backup names can be unordered so we should try to retrieve
        # any backup from backup_names list
        def _get_current_backup_name():
            rows = tab_backups.table_backups.rows
            assert_that(rows, has_length(1))

            backup_name = rows[0].cell('name').value
            assert_that(backup_name, is_in(backup_names))

            return backup_name

        backup_name = _get_current_backup_name()
        ordered_names.append(backup_name)

        assert_that(tab_backups.table_backups.link_next.is_present,
                    equal_to(True))
        assert_that(tab_backups.table_backups.link_prev.is_present,
                    equal_to(False))

        # check all elements except for the first and the last
        for _ in range(1, count - 1):
            tab_backups.table_backups.link_next.click()
            backup_name = _get_current_backup_name()
            ordered_names.append(backup_name)

            assert_that(tab_backups.table_backups.link_next.is_present,
                        equal_to(True))
            assert_that(tab_backups.table_backups.link_prev.is_present,
                        equal_to(True))

        tab_backups.table_backups.link_next.click()
        backup_name = _get_current_backup_name()
        ordered_names.append(backup_name)

        assert_that(tab_backups.table_backups.link_next.is_present,
                    equal_to(False))
        assert_that(tab_backups.table_backups.link_prev.is_present,
                    equal_to(True))

        # check that all created volume names have been checked
        assert_that(ordered_names, contains_inanyorder(*backup_names))

        for i in range(count - 2, 0, -1):
            tab_backups.table_backups.link_prev.click()
            tab_backups.table_backups.row(
                name=ordered_names[i]).wait_for_presence(30)

            assert_that(tab_backups.table_backups.link_next.is_present,
                        equal_to(True))
            assert_that(tab_backups.table_backups.link_prev.is_present,
                        equal_to(True))

        tab_backups.table_backups.link_prev.click()
        tab_backups.table_backups.row(
            name=ordered_names[0]).wait_for_presence(30)

        assert_that(tab_backups.table_backups.link_next.is_present,
                    equal_to(True))
        assert_that(tab_backups.table_backups.link_prev.is_present,
                    equal_to(False))

    @steps_checker.step
    def check_backup_creation_form_name_field_max_length(self, volume_name,
                                                         expected_length):
        """Step to check max possible length of backup name input.

        Args:
            volume_name (str): name of volume to open backup creating form on
                it
            expected_length (int): expected max form field length

        Raises:
            AssertionError: if actual max length is not equal to
                `expected_length`
        """
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_create_backup.click()

        with tab_volumes.form_create_backup as form:
            form.field_name.value = 'a' * (expected_length + 1)
            backup_name = form.field_name.value
            form.cancel()
        assert_that(backup_name, has_length(expected_length))

    @steps_checker.step
    def check_snapshot_creation_form_name_field_max_length(self, volume_name,
                                                           expected_length):
        """Step to check max length of snapshot creation form name input.

        Args:
            volume_name (str): name of volume to open snapshot create form on
                it
            expected_length (int): expected max form field length

        Raises:
            AssertionError: if actual max length is not equal to
                `expected_length`
        """
        tab_volumes = self._tab_volumes()

        with tab_volumes.table_volumes.row(
                name=volume_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_create_snapshot.click()

        with tab_volumes.form_create_snapshot as form:
            form.field_name.value = 'a' * (expected_length + 1)
            snapshot_name = form.field_name.value
            form.cancel()
        assert_that(snapshot_name, has_length(expected_length))
