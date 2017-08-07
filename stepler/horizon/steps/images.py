"""
------------
Images steps
------------
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

from hamcrest import (assert_that, contains_inanyorder, equal_to, greater_than,
                      has_entries, has_length, is_in, is_not)  # noqa
from selenium.webdriver.common.keys import Keys
from time import sleep

from stepler import config
from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter


class ImagesSteps(base.BaseSteps):
    """Images steps."""

    def _page_images(self):
        """Open images page if it isn't opened."""
        return self._open(self.app.page_images)

    @steps_checker.step
    def create_image(self,
                     image_name,
                     image_description=None,
                     image_url=config.CIRROS_QCOW2_URL,
                     image_file=None,
                     disk_format='QCOW2',
                     min_disk=None,
                     min_ram=None,
                     protected=False,
                     big_image=False,
                     check=True):
        """Step to create image.

        Args:
            image_name (str): image name
            image_description (object|None): image description
            image_url (str): URL of image location
            image_file (str): path of image file
            disk_format (str): disk format
            min_disk (int): min disk size (in Gb)
            min_ram (int): min RAM size (in Mb)
            protected (bool): indicator whether image is protected or not
            big_image (bool): indicator whether image has big size or not
            check (bool): flag whether to check step or not
        """
        page_images = self._page_images()
        page_images.button_create_image.click()

        if image_url:
            image_file = utils.get_file_path(image_url)
            image_url = None

        with page_images.form_create_image as form:
            form.field_name.value = image_name

            form.button_group_source_type.value = 'File'
            form.field_image_file.value = image_file

            if image_description:
                form.field_description.value = image_description

            if min_disk:
                form.field_min_disk.value = min_disk

            if min_ram:
                form.field_min_ram.value = min_ram

            if protected:
                form.button_group_protected.value = "Yes"
            else:
                form.button_group_protected.value = "No"

            form.combobox_disk_format.value = disk_format

            if big_image:
                form.submit(modal_timeout=config.LONG_ACTION_TIMEOUT)
            else:
                form.submit()

        if check:
            self.close_notification('success')

            def _check_image_active():
                # workaround for bug
                # https://bugs.launchpad.net/mos/+bug/1675786
                self.refresh_page()
                try:
                    page_images.table_images.row(
                        name=image_name).wait_for_status(config.STATUS_ACTIVE,
                                                         timeout=0)
                    return True
                except waiter.TimeoutExpired:
                    return False

            if big_image:
                waiter.wait(_check_image_active,
                            timeout_seconds=config.LONG_EVENT_TIMEOUT)
            else:
                waiter.wait(_check_image_active,
                            timeout_seconds=config.EVENT_TIMEOUT)

    @steps_checker.step
    def delete_image(self, image_name, check=True):
        """Step to delete image."""
        page_images = self._page_images()

        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_images.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_images.table_images.row(
                name=image_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def delete_images(self, image_names, check=True):
        """Step to delete images."""
        page_images = self._page_images()

        for image_name in image_names:
            page_images.table_images.row(
                name=image_name).checkbox.select()

        page_images.button_delete_images.click()

        # if some of images can't be deleted - modal won't show
        try:
            page_images.form_confirm.wait_for_presence()
            page_images.form_confirm.submit()
        except Exception:
            pass

        if check:
            self.close_notification('success')
            for image_name in image_names:
                page_images.table_images.row(
                    name=image_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def add_metadata(self, image_name, metadata, check=True):
        """Step to add image metadata.

        Args:
            image_name (str): image name
            metadata (dict): image metadata {name: value}
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if image status is not 'Active'
            AssertionError: if check failed
        """
        page_images = self._page_images()
        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_update_metadata.click()

        with page_images.form_update_metadata as form:
            for metadata_name, metadata_value in metadata.items():
                form.field_metadata_name.value = metadata_name
                form.button_add_metadata.click()
                form.list_metadata.row(
                    metadata_name).field_metadata_value.value = metadata_value

            form.submit()

        if check:
            page_images.table_images.row(
                name=image_name).wait_for_status(config.STATUS_ACTIVE)
            image_metadata = self.get_metadata(image_name)
            image_metadata.pop('direct_url', None)
            assert_that(metadata, equal_to(image_metadata))

    @steps_checker.step
    def delete_metadata(self, image_name, metadata, check=True):
        """Step to delete metadata.

        Args:
            image_name (str): image name
            metadata (dict): image metadata {name: value}
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if image status is not 'Active'
        """
        page_images = self._page_images()
        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_update_metadata.click()

        with page_images.form_update_metadata as form:
            for metadata_name in metadata:
                form.existing_metadata_filter.value = metadata_name
                form.button_delete_metadata.click()

            form.submit()

        if check:
            page_images.table_images.row(
                name=image_name).wait_for_status(config.STATUS_ACTIVE)

    @steps_checker.step
    def get_metadata(self, image_name):
        """Step to get image metadata."""
        metadata = {}

        page_images = self._page_images()

        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_update_metadata.click()

        for row in page_images.form_update_metadata.list_metadata.rows:
            metadata[row.field_metadata_name.value] = (
                row.field_metadata_value.value)

        page_images.form_update_metadata.cancel()

        return metadata

    @steps_checker.step
    def update_image(self, image_name, new_image_name=None,
                     description=None, min_disk=None,
                     min_ram=None, protected=False,
                     check=True):
        """Step to update image.

        Args:
            image_name (str): image name
            new_image_name (str): new image name
            description (str|None): image description
            metadata (dict|None): image metadata {name: value} (max = 2 keys)
            min_disk (int|None): minimal disk size
            min_ram (int|None): minimal ram
            protected (bool): flag whether to set protected or not
            check (bool): flag whether to check step or not

         Raises:
            TimeoutExpired: if no 'Success' message or image status is not
                'Active'
        """
        page_images = self._page_images()

        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_edit.click()

        with page_images.form_update_image as form:

            if new_image_name:
                form.field_name.value = new_image_name

            if description:
                form.field_description.value = description

            if min_disk is not None:
                form.field_min_disk.value = min_disk

            if min_ram is not None:
                form.field_min_ram.value = min_ram

            if protected:
                form.button_group_protected.value = "Yes"
            else:
                form.button_group_protected.value = "No"

            form.submit()

        if check:
            self.close_notification('success')

            page_images.table_images.row(
                name=image_name).wait_for_status(config.STATUS_ACTIVE)

    @steps_checker.step
    def view_image(self, image_name, check=True):
        """Step to view image."""
        self._page_images().table_images.row(
            name=image_name).link_image.click()

        self.app.page_image.image_info_main.wait_for_presence()

        if check:
            assert_that(
                self.app.page_image.label_name.value,
                equal_to(image_name))

    @steps_checker.step
    def create_volume(self, image_name, volume_name, check=True):
        """Step to create volume from image."""
        page_images = self._page_images()

        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_create_volume.click()

        with page_images.form_create_volume as form:
            form.field_name.value = volume_name
            form.submit()

            if check:
                self.close_notification('success')
                form.wait_for_absence()

    @steps_checker.step
    def launch_instance(self, image_name, instance_name, network_name,
                        flavor, check=True):
        """Step to launch instance from image."""
        page_images = self._page_images()
        flavor_name = flavor or config.HORIZON_TEST_FLAVOR

        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.item_default.click()

        with page_images.form_launch_instance as form:

            with form.tab_details as tab:
                tab.field_name.value = instance_name

            form.item_flavor.click()
            with form.tab_flavor as tab:
                tab.table_available_flavors.row(
                    name=flavor_name).button_add.click()

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
    def check_images_pagination(self, image_names):
        """Step to check images pagination."""
        assert_that(image_names, has_length(greater_than(2)))

        ordered_names = []
        count = len(image_names)
        page_images = self._page_images()

        # image names can be unordered so we should try to retrieve
        # any image from image_names list
        def _get_current_image_name():
            rows = page_images.table_images.rows
            assert_that(rows, has_length(1))

            image_name = rows[0].cell('name').value
            assert_that(image_name, is_in(image_names))

            return image_name

        image_name = _get_current_image_name()
        ordered_names.append(image_name)

        assert_that(page_images.table_images.link_next.is_present,
                    equal_to(True))
        assert_that(page_images.table_images.link_prev.is_present,
                    equal_to(False))

        # check all elements except for the first and the last
        for _ in range(1, count - 1):
            page_images.table_images.link_next.click()
            image_name = _get_current_image_name()
            ordered_names.append(image_name)

            assert_that(page_images.table_images.link_next.is_present,
                        equal_to(True))
            assert_that(page_images.table_images.link_prev.is_present,
                        equal_to(True))

        page_images.table_images.link_next.click()
        volume_name = _get_current_image_name()
        ordered_names.append(volume_name)

        assert_that(page_images.table_images.link_next.is_present,
                    equal_to(False))
        assert_that(page_images.table_images.link_prev.is_present,
                    equal_to(True))

        page_images.table_images.link_prev.click()
        page_images.table_images.row(name=image_names[1]).wait_for_presence()

        assert_that(page_images.table_images.link_next.is_present,
                    equal_to(True))
        assert_that(page_images.table_images.link_prev.is_present,
                    equal_to(True))

        # check that all created image names have been checked
        assert_that(ordered_names, contains_inanyorder(*image_names))

        for i in range(count - 2, 0, -1):
            page_images.table_images.link_prev.click()
            page_images.table_images.row(
                name=ordered_names[i]).wait_for_presence()

            assert_that(page_images.table_images.link_next.is_present,
                        equal_to(True))
            assert_that(page_images.table_images.link_prev.is_present,
                        equal_to(True))

        page_images.table_images.link_prev.click()
        page_images.table_images.row(name=ordered_names[0]).wait_for_presence()

        assert_that(page_images.table_images.link_next.is_present,
                    equal_to(True))
        assert_that(page_images.table_images.link_prev.is_present,
                    equal_to(False))

    @steps_checker.step
    def check_image_present(self, image_name, timeout=None):
        """Step to check image is present."""
        self._page_images().table_images.row(
            name=image_name).wait_for_presence(timeout)

    @steps_checker.step
    def check_flavors_limited_in_launch_instance_form(self, image_name,
                                                      disk_size, ram_size):
        """Step to check flavors are limited in launch instance form."""
        with self._page_images() as page:
            page.table_images.row(
                name=image_name).dropdown_menu.item_default.click()

            with page.form_launch_instance as form:
                form.item_flavor.click()
                waiter.wait(
                    lambda: (form.tab_flavor.table_available_flavors.rows,
                             "No available flavors"),
                    timeout_seconds=30,
                    sleep_seconds=0.1)

                for row in form.tab_flavor.table_available_flavors.rows:

                    ram_cell = row.cell('ram')
                    if utils.get_size(ram_cell.value, to='mb') < ram_size:
                        assert_that(ram_cell.label_alert.is_present,
                                    equal_to(True))
                    else:
                        assert_that(ram_cell.label_alert.is_present,
                                    equal_to(False))

                    disk_cell = row.cell('root_disk')
                    if utils.get_size(disk_cell.value, to='gb') < disk_size:
                        assert_that(disk_cell.label_alert.is_present,
                                    equal_to(True))
                    else:
                        assert_that(disk_cell.label_alert.is_present,
                                    equal_to(False))
                form.cancel()

    @steps_checker.step
    def check_public_image_visible(self, image_name):
        """Step to check public image is visible."""
        with self._page_images() as page:
            page.open()
            page.search_bar.apply('Visibility', 'Public')
            page.table_images.row(name=image_name).wait_for_presence()
            page.search_bar.clear('Visibility')

    @steps_checker.step
    def check_non_public_image_not_visible(self, image_name):
        """Step to check non-public image is not visible for other projects.

        Args:
            image_name (str): image name

        Raises:
            AssertionError: if image is available in public images list
        """
        with self._page_images() as page:
            page.search_bar.apply('Visibility', 'Public')
            assert_that(page.table_images.row(name=image_name).is_present,
                        equal_to(False))
            page.search_bar.clear('Visibility')

    @steps_checker.step
    def check_image_info(self,
                         image_name,
                         expected_description=None,
                         expected_metadata=None):
        """Step to check image detailed info.

        This step checks that values of description/metadata in detailed info
        are correct. For 'None' values, these data must be missing.

        Args:
            image_name (str): image name
            expected_description (str|None): expected image description
            expected_metadata (dict|None): expected image metadata
                {name: value} (max = 2 keys)

        Raises:
            AssertionError: if real and expected data are different
        """
        table = self._page_images().table_images.row(name=image_name)
        table.link_image.click()

        properties = self.app.page_image.image_info_custom.properties

        description = properties.pop('Description', None)

        assert_that(description, equal_to(expected_description))
        assert_that(properties, has_entries(**(expected_metadata or {})))

    @steps_checker.step
    def open_link_in_new_tab(self, image_name, check=True):
        """Step to open link of image info in new tab.

        Args:
            image_name (str): image name
        """
        main_page = self._page_images()
        link_to_click = main_page.table_images.row(name=image_name).webdriver
        sleep(10)
        link_to_click.find_element_by_partial_link_text(image_name).send_keys(
            Keys.CONTROL + Keys.RETURN)

    @steps_checker.step
    def switch_to_new_tab(self, check=True):
        """Step to switch to new tab."""
        main_page = self.app.page_images
        main_page.webdriver.find_element_by_tag_name('body').send_keys(
            Keys.CONTROL + Keys.TAB)
        page = main_page.webdriver.current_window_handle
        main_page.webdriver.switch_to_window(page)

    @steps_checker.step
    def check_page_is_available(self, image_name, check=True):
        """Step to check page is available and then close it.

        Args:
            image_name: image name
        """
        main_page = self.app.page_images
        assert_that(main_page, is_not(None))
        image_page = self.app.page_image
        image_page.image_info_main.wait_for_presence()
        assert_that(image_page.label_name.value, equal_to(image_name))
        # close current page
        main_page.webdriver.find_element_by_tag_name('body').send_keys(
            Keys.CONTROL + 'w')

