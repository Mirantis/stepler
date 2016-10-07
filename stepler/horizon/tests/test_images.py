"""
-----------
Image tests
-----------
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

import pytest

from stepler.horizon import config
from stepler.horizon.utils import generate_ids, generate_files  # noqa


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any one."""

    @pytest.mark.parametrize('images_count', [1, 2])
    def test_delete_images(self, images_count, create_images):
        """Verify that user can delete images as batch."""
        image_names = list(
            generate_ids('image', count=images_count, length=20))
        create_images(*image_names)

    def test_create_image_from_local_file(self, create_image):
        """Verify that user can create image from local file."""
        image_name = next(generate_ids('image', length=20))
        image_file = next(generate_files(postfix='.qcow2'))
        create_image(image_name, image_file)

    def test_view_image(self, image, images_steps):
        """Verify that user can view image info."""
        images_steps.view_image(image.name)

    def test_images_pagination(self, images_steps, create_images,
                               update_settings):
        """Verify images pagination works right and back."""
        image_names = sorted(list(generate_ids('image', count=2, length=20)))
        create_images(*image_names)
        update_settings(items_per_page=1)
        # TODO(schipiga): move it to check step
        # page_images = images_steps.page_images()
        # page_images.table_images.row(name=image_names[0]).wait_for_presence()
        # assert page_images.table_images.link_next.is_present
        # assert not page_images.table_images.link_prev.is_present

        # page_images.table_images.link_next.click()

        # page_images.table_images.row(name=image_names[1]).wait_for_presence()
        # assert page_images.table_images.link_next.is_present
        # assert page_images.table_images.link_prev.is_present

        # page_images.table_images.link_next.click()

        # page_images.table_images.row(name='TestVM').wait_for_presence()
        # assert not page_images.table_images.link_next.is_present
        # assert page_images.table_images.link_prev.is_present

        # page_images.table_images.link_prev.click()

        # page_images.table_images.row(name=image_names[1]).wait_for_presence()
        # assert page_images.table_images.link_next.is_present
        # assert page_images.table_images.link_prev.is_present

        # page_images.table_images.link_prev.click()

        # page_images.table_images.row(name=image_names[0]).wait_for_presence()
        # assert page_images.table_images.link_next.is_present
        # assert not page_images.table_images.link_prev.is_present

    def test_update_image_metadata(self, image, images_steps):
        """Verify that user can update image metadata."""
        metadata = {
            next(generate_ids('metadata')): next(generate_ids("value"))
            for _ in range(2)}
        images_steps.update_metadata(image.name, metadata)
        image_metadata = images_steps.get_metadata(image.name)
        assert metadata == image_metadata

    def test_remove_protected_image(self, horizon, create_image, images_steps):
        """Verify that user can't delete protected image."""
        image_name = next(generate_ids('image', length=20))
        create_image(image_name, protected=True)
        images_steps.delete_images([image_name], check=False)
        images_steps.close_notification('error')
        # TODO(schipiga): move it to check step
        # horizon.page_images.table_images.row(
        #     name=image_name).wait_for_presence()
        images_steps.update_image(image_name, protected=False)

    def test_edit_image(self, image, images_steps):
        """Verify that user can edit image."""
        new_image_name = image.name + '(updated)'
        with image.put(name=new_image_name):
            images_steps.update_image(image.name, new_image_name)

    def test_create_volume_from_image(self, image, images_steps,
                                      volumes_steps):
        """Verify that user can create volume from image."""
        volume_name = next(generate_ids('volume'))
        images_steps.create_volume(image.name, volume_name)

        # TODO(schipiga): move it to check step
        # volumes_steps.tab_volumes().table_volumes.row(
        #     name=volume_name, status='Available').wait_for_presence(90)
        volumes_steps.delete_volume(volume_name)

    def test_set_image_disk_and_ram_size(self, horizon, create_image):
        """Verify that image limits has influence to flavor choice."""
        ram_size = 1024
        disk_size = 4

        image_name = next(generate_ids('image', length=20))
        create_image(image_name, min_disk=disk_size, min_ram=ram_size)
        # TODO(schipiga): move it to check step
        # with horizon.page_images as page:
        #     page.table_images.row(
        #         name=image_name).dropdown_menu.item_default.click()

        #     with page.form_launch_instance as form:
        #         form.item_flavor.click()
        #         wait(lambda: form.tab_flavor.table_available_flavors.rows,
        #              timeout_seconds=30, sleep_seconds=0.1)

        #         for row in form.tab_flavor.table_available_flavors.rows:

        #             ram_cell = row.cell('ram')
        #             if get_size(ram_cell.value, to='mb') < ram_size:
        #                 assert ram_cell.label_alert.is_present
        #             else:
        #                 assert not ram_cell.label_alert.is_present

        #             disk_cell = row.cell('root_disk')
        #             if get_size(disk_cell.value, to='gb') < disk_size:
        #                 assert disk_cell.label_alert.is_present
        #             else:
        #                 assert not disk_cell.label_alert.is_present
        #         form.cancel()

    def test_public_image_visibility(self, horizon, login):
        """Verify that public image is visible for other users."""
        # TODO(schipiga): move it to check step
        # with horizon.page_images as page:
        #     page.open()
        #     page.button_public_images.click()
        #     page.table_images.row(name='TestVM').wait_for_presence()

    def test_launch_instance_from_image(self, image, images_steps,
                                        instances_steps):
        """Verify that user can launch instance from image."""
        instance_name = next(generate_ids('instance'))
        images_steps.launch_instance(image.name, instance_name,
                                     network_name=config.INTERNAL_NETWORK_NAME)
        # TODO(schipiga): move it to check step
        # instances_steps.page_instances().table_instances.row(
        #     name=instance_name).wait_for_status('Active')
        instances_steps.delete_instance(instance_name)
