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
        images_steps.check_images_pagination(image_names)

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
        images_steps.check_image_present(image_name)
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
        volumes_steps.check_volume_present(volume_name, timeout=90)
        volumes_steps.delete_volume(volume_name)

    def test_set_image_disk_and_ram_size(self, create_image, images_steps):
        """Verify that image limits has influence to flavor choice."""
        ram_size = 1024
        disk_size = 4

        image_name = next(generate_ids('image', length=20))
        create_image(image_name, min_disk=disk_size, min_ram=ram_size)
        images_steps.check_flavors_limited_in_launch_instance_form(image_name,
                                                                   disk_size,
                                                                   ram_size)

    def test_public_image_visibility(self, images_steps):
        """Verify that public image is visible for other users."""
        images_steps.check_public_image_visible('TestVM')

    def test_launch_instance_from_image(self, image, images_steps,
                                        instances_steps):
        """Verify that user can launch instance from image."""
        instance_name = next(generate_ids('instance'))
        images_steps.launch_instance(image.name, instance_name,
                                     network_name=config.INTERNAL_NETWORK_NAME)
        instances_steps.check_instance_active(instance_name)
        instances_steps.delete_instance(instance_name)
