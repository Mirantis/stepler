"""
Images steps.

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
from hamcrest import assert_that, equal_to  # noqa

from stepler.horizon.config import EVENT_TIMEOUT
from stepler.third_party.steps_checker import step

from .base import BaseSteps

CIRROS_URL = ('http://download.cirros-cloud.net/0.3.1/'
              'cirros-0.3.1-x86_64-uec.tar.gz')


class ImagesSteps(BaseSteps):
    """Images steps."""

    def _page_images(self):
        """Open images page if it isn't opened."""
        return self._open(self.app.page_images)

    @step
    @pom.timeit('Step')
    def create_image(self, image_name, image_url=CIRROS_URL, image_file=None,
                     disk_format='QCOW2', min_disk=None, min_ram=None,
                     protected=False, check=True):
        """Step to create image."""
        page_images = self._page_images()
        page_images.button_create_image.click()

        with page_images.form_create_image as form:
            form.field_name.value = image_name

            if image_file:
                form.combobox_source_type.value = 'Image File'
                form.field_image_file.value = image_file

            else:
                form.combobox_source_type.value = 'Image Location'
                form.field_image_url.value = image_url

            if min_disk:
                form.field_min_disk.value = min_disk

            if min_ram:
                form.field_min_ram.value = min_ram

            if protected:
                form.checkbox_protected.select()
            else:
                form.checkbox_protected.unselect()

            form.combobox_disk_format.value = disk_format
            form.submit()

        if check:
            self.close_notification('info')
            page_images.table_images.row(
                name=image_name).wait_for_status('Active')

    @step
    @pom.timeit('Step')
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
                name=image_name).wait_for_absence(EVENT_TIMEOUT)

    @step
    @pom.timeit('Step')
    def delete_images(self, image_names, check=True):
        """Step to delete images."""
        page_images = self._page_images()

        for image_name in image_names:
            page_images.table_images.row(
                name=image_name).checkbox.select()

        page_images.button_delete_images.click()
        page_images.form_confirm.submit()

        if check:
            self.close_notification('success')
            for image_name in image_names:
                page_images.table_images.row(
                    name=image_name).wait_for_absence(EVENT_TIMEOUT)

    @step
    @pom.timeit('Step')
    def update_metadata(self, image_name, metadata, check=True):
        """Step to update image metadata."""
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
                name=image_name, status='Active').wait_for_presence()

    @step
    @pom.timeit('Step')
    def get_metadata(self, image_name):
        """Step to get image metadata."""
        metadata = {}

        page_images = self._page_images()

        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_update_metadata.click()

        for row in page_images.form_update_metadata.list_metadata.rows:
            metadata[row.field_metadata_name.value] = \
                row.field_metadata_value.value

        page_images.form_update_metadata.cancel()

        return metadata

    @step
    @pom.timeit('Step')
    def update_image(self, image_name, new_image_name=None, protected=False,
                     check=True):
        """Step to update image."""
        page_images = self._page_images()

        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_edit.click()

        with page_images.form_update_image as form:

            if new_image_name:
                form.field_name.value = new_image_name

            if protected:
                form.checkbox_protected.select()
            else:
                form.checkbox_protected.unselect()

            form.submit()

        if check:
            self.close_notification('success')

            page_images.table_images.row(
                name=new_image_name or image_name,
                status='Active').wait_for_presence()

    @step
    @pom.timeit('Step')
    def view_image(self, image_name, check=True):
        """Step to view image."""
        self._page_images().table_images.row(
            name=image_name).link_image.click()

        if check:
            assert_that(self.app.page_image.info_image.label_name.value,
                        equal_to(image_name))

    @step
    @pom.timeit('Step')
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
                self.close_notification('info')
                form.wait_for_absence()

    @step
    @pom.timeit('Step')
    def launch_instance(self, image_name, instance_name, network_name,
                        check=True):
        """Step to launch instance from image."""
        page_images = self._page_images()

        with page_images.table_images.row(
                name=image_name).dropdown_menu as menu:
            menu.item_default.click()

        with page_images.form_launch_instance as form:

            with form.tab_details as tab:
                tab.field_name.value = instance_name

            form.item_flavor.click()
            with form.tab_flavor as tab:
                tab.table_available_flavors.row(
                    name='m1.tiny').button_add.click()

            form.item_network.click()
            with form.tab_network as tab:
                tab.table_available_networks.row(
                    name=network_name).button_add.click()

            form.submit()

            if check:
                form.wait_for_absence()
