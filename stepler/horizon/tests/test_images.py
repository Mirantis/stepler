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
from stepler.third_party import utils


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any one."""

    @pytest.mark.parametrize('images_count', [1, 2])
    @pytest.mark.idempotent_id('a54b457e-f3b2-4903-9702-b9e75ede5830')
    def test_delete_images(self, images_count, create_images):
        """Verify that user can delete images as batch."""
        image_names = list(
            generate_ids(count=images_count, length=20))
        create_images(*image_names)

    @pytest.mark.idempotent_id('6c0cc571-857f-4846-a2b9-2a08c8ab3a14')
    def test_create_image_from_local_file(self, create_image):
        """Verify that user can create image from local file."""
        image_name = next(generate_ids(length=20))
        image_file = next(generate_files(postfix='.qcow2'))
        create_image(image_name, image_file=image_file)

    @pytest.mark.idempotent_id('c4cf3c6d-45d2-4629-b9fe-3e8eed3f1e59')
    def test_view_image(self, image, images_steps):
        """Verify that user can view image info."""
        images_steps.view_image(image.name)

    @pytest.mark.idempotent_id('b39a1540-f500-4f86-b123-e89262a51670')
    def test_images_pagination(self, images_steps, create_images,
                               update_settings):
        """Verify images pagination works right and back."""
        image_names = sorted(list(generate_ids(count=2, length=20)))
        create_images(*image_names)
        update_settings(items_per_page=1)
        images_steps.check_images_pagination(image_names)

    @pytest.mark.idempotent_id('b835ce2b-41b2-4d7a-8b8f-139163234852')
    def test_update_image_metadata(self, image, images_steps):
        """Verify that user can update image metadata."""
        metadata = {
            next(generate_ids('metadata')): next(generate_ids("value"))
            for _ in range(2)}
        images_steps.add_metadata(image.name, metadata)
        image_metadata = images_steps.get_metadata(image.name)
        assert metadata == image_metadata

    @pytest.mark.idempotent_id('4016e9af-257b-4df2-8c63-5716f134e5bb')
    def test_remove_protected_image(self, create_image, images_steps):
        """Verify that user can't delete protected image."""
        image_name = next(generate_ids(length=20))
        create_image(image_name, protected=True)
        images_steps.delete_images([image_name], check=False)
        images_steps.close_notification('error')
        images_steps.check_image_present(image_name)
        images_steps.update_image(image_name, protected=False)

    @pytest.mark.idempotent_id('50dcf89e-370a-47d2-a0eb-c56dd77c968e')
    def test_edit_image(self, image, images_steps):
        """Verify that user can edit image."""
        new_image_name = image.name + '(updated)'
        with image.put(name=new_image_name):
            images_steps.update_image(image.name, new_image_name)

    @pytest.mark.idempotent_id('619298ae-f9f5-4afa-a50b-c3f5faa38c81')
    def test_create_volume_from_image(self, image, images_steps,
                                      volumes_steps_ui):
        """Verify that user can create volume from image."""
        volume_name = next(generate_ids())
        images_steps.create_volume(image.name, volume_name)
        volumes_steps_ui.check_volume_present(volume_name, timeout=90)
        volumes_steps_ui.delete_volume(volume_name)

    @pytest.mark.idempotent_id('3167e844-1d13-44d5-aa1e-85c58c086240')
    def test_set_image_disk_and_ram_size(self, create_image, images_steps):
        """Verify that image limits has influence to flavor choice."""
        ram_size = 1024
        disk_size = 4

        image_name = next(generate_ids(length=20))
        create_image(image_name, min_disk=disk_size, min_ram=ram_size)
        images_steps.check_flavors_limited_in_launch_instance_form(image_name,
                                                                   disk_size,
                                                                   ram_size)

    @pytest.mark.idempotent_id('f5339379-2e89-4adf-9074-78ed3c7e9a4e')
    def test_public_image_visibility(self, images_steps):
        """Verify that public image is visible for other users."""
        images_steps.check_public_image_visible('TestVM')

    @pytest.mark.idempotent_id('3c98d922-df89-4701-a4b1-c5258fda5d7b')
    def test_launch_instance_from_image(self, image, images_steps,
                                        instances_steps):
        """Verify that user can launch instance from image."""
        instance_name = next(generate_ids())
        images_steps.launch_instance(image.name, instance_name,
                                     network_name=config.INTERNAL_NETWORK_NAME)
        instances_steps.check_instance_active(instance_name)
        instances_steps.delete_instance(instance_name)

    @pytest.mark.idempotent_id('db36570f-c87e-4629-a83b-80eed6cbcab3')
    def test_edit_image_description(self, image, images_steps):
        """**Scenario:** Check addition of image description.

        **Setup:**

        #. Create image

        **Steps:**

        #. Click on image and check that description is missing
        #. Edit image by adding description
        #. Click on image and check description in detailed info

        **Teardown:**

        #. Delete image
        """
        images_steps.check_image_info(image.name, expected_description=None)
        image_description = next(generate_ids())
        images_steps.update_image(image.name, description=image_description)
        images_steps.check_image_info(image.name,
                                      expected_description=image_description)

    @pytest.mark.idempotent_id('c42d793b-efa9-46c4-b031-9f7bf7a49cd1')
    def test_edit_image_disk_and_ram(self, image, images_steps,
                                     instances_steps):
        """**Scenario:** Check edition of minimum disk and RAM.

        **Setup:**

        #. Create image

        **Steps:**

        #. Edit image and set Minimum Disk = 60Gb and Minimum RAM = 0
        #. Try to launch instance
        #. Check that all flavors with disk < 60Gb are unavailable
        #. Edit image and set Minimum Disk = 0Gb and Minimum RAM = 4096Mb
        #. Try to launch instance
        #. Check that all flavors with ram < 4096Mb are unavailable

        **Teardown:**

        #. Delete image
        """
        for min_disk, min_ram in [(60, 0), (0, 4096)]:
            images_steps.update_image(image.name, min_disk=min_disk,
                                      min_ram=min_ram)
            images_steps.check_flavors_limited_in_launch_instance_form(
                image.name, min_disk, min_ram)

    @pytest.mark.idempotent_id('e0aec971-00ea-41a4-9369-fc6ef3ea774d')
    def test_add_delete_image_metadata(self, image, images_steps):
        """**Scenario:** Check addition and deletion of image metadata.

        **Setup:**

        #. Create image

        **Steps:**

        #. Check that no metadata in Custom properties
        #. Add metadata
        #. Check that metadata appeared in Custom properties and values are
           correct
        #. Delete metadata
        #. Check that metadata disappeared in Custom properties

        **Teardown:**

        #. Delete image
        """
        images_steps.check_image_info(image.name, expected_metadata=None)

        metadata = {
            next(generate_ids('metadata')): next(generate_ids("value"))
            for _ in range(2)}
        images_steps.add_metadata(image.name, metadata)
        images_steps.check_image_info(image.name, expected_metadata=metadata)

        images_steps.delete_metadata(image.name, metadata)
        images_steps.check_image_info(image.name, expected_metadata=None)


@pytest.mark.usefixtures('user_only')
class TestUserOnly(object):
    """Tests for user only."""

    @pytest.mark.idempotent_id('451ea18f-e513-48ac-999a-4e719516478e')
    def test_image_privacy(self, glance_steps, images_steps,
                           auth_steps):
        """Verify that non public image is not visible for other users.

        **Setup:**

        #. Login as user to another project

        **Steps:**

        #. Create image with public=False as admin via API
        #. Check that image is not available as public image

        **Teardown:**

        #. Delete image
        """
        image = glance_steps.create_images(
            utils.get_file_path(config.CIRROS_QCOW2_URL),
            image_names=utils.generate_ids(length=20))[0]
        images_steps.check_non_public_image_not_visible(image.name)

    # the following test is executed only for one user because of its long
    # duration (> 1 hour)
    # TODO(ssokolov) add some mark for specific environment and execution time
    @pytest.mark.idempotent_id('b846cf53-d3fa-4cca-8b10-fbaf50749f7c')
    def test_big_image_create_delete(self, create_image):
        """**Scenario:** Check big image creation and deletion from file.

        **Steps:**

        #. Create file 100Gb
        #. Create image from this file
        #. Delete big file

        **Teardown:**

        #. Delete image
        """
        image_name = next(utils.generate_ids(length=20))
        with utils.generate_file_context(
                postfix='.qcow2', size=config.BIG_FILE_SIZE) as file_path:
            create_image(image_name, image_file=file_path, big_image=True)
