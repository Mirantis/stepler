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

from stepler import config
from stepler.third_party import utils


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any one."""

    @pytest.mark.idempotent_id('a54b457e-f3b2-4903-9702-b9e75ede5830',
                               any_one='admin', images_count=1)
    @pytest.mark.idempotent_id('6094e9bf-67dd-4f19-a0a3-73cf7b91603a',
                               any_one='admin', images_count=2)
    @pytest.mark.idempotent_id('083edf5e-ba16-414a-854d-d0ddcbbe7186',
                               any_one='user', images_count=1)
    @pytest.mark.idempotent_id('ace4a999-9318-4446-a957-57143e52703d',
                               any_one='user', images_count=2)
    @pytest.mark.parametrize('images_count', [1, 2])
    def test_delete_images(self, images_count, create_images):
        """Verify that user can delete images as batch."""
        image_names = list(
            utils.generate_ids(count=images_count, length=20))
        create_images(*image_names)

    @pytest.mark.idempotent_id('6c0cc571-857f-4846-a2b9-2a08c8ab3a14',
                               any_one='admin')
    @pytest.mark.idempotent_id('8a17f2d4-42fd-46e7-a066-ace6b0b161ae',
                               any_one='user')
    def test_create_image_from_local_file(self, create_image):
        """Verify that user can create image from local file."""
        image_name = next(utils.generate_ids(length=20))
        image_file = next(utils.generate_files(postfix='.qcow2'))
        create_image(image_name, image_file=image_file)

    @pytest.mark.idempotent_id('c4cf3c6d-45d2-4629-b9fe-3e8eed3f1e59',
                               any_one='admin')
    @pytest.mark.idempotent_id('a7330cae-30ea-4131-a819-42a71f87576d',
                               any_one='user')
    def test_view_image(self, image, images_steps):
        """Verify that user can view image info."""
        images_steps.view_image(image.name)

    @pytest.mark.idempotent_id('b39a1540-f500-4f86-b123-e89262a51670',
                               any_one='admin')
    @pytest.mark.idempotent_id('2454c803-bc07-44c7-b842-0151c510c7d2',
                               any_one='user')
    def test_images_pagination(self, images_steps, create_images,
                               update_settings):
        """Verify images pagination works right and back."""
        image_names = sorted(list(utils.generate_ids(count=2, length=20)))
        create_images(*image_names)
        update_settings(items_per_page=1)
        images_steps.check_images_pagination(image_names)

    @pytest.mark.idempotent_id('b835ce2b-41b2-4d7a-8b8f-139163234852',
                               any_one='admin')
    @pytest.mark.idempotent_id('1b439ae8-32aa-476d-abf9-3e2ae796de46',
                               any_one='user')
    def test_update_image_metadata(self, image, images_steps):
        """Verify that user can update image metadata."""
        metadata = {next(utils.generate_ids('metadata')):
                    next(utils.generate_ids("value"))
                    for _ in range(2)}
        images_steps.add_metadata(image.name, metadata)
        image_metadata = images_steps.get_metadata(image.name)
        assert metadata == image_metadata

    @pytest.mark.idempotent_id('4016e9af-257b-4df2-8c63-5716f134e5bb',
                               any_one='admin')
    @pytest.mark.idempotent_id('637b39da-5648-4d46-bf3f-d51ca858928f',
                               any_one='user')
    def test_remove_protected_image(self, create_image, images_steps):
        """Verify that user can't delete protected image."""
        image_name = next(utils.generate_ids(length=20))
        create_image(image_name, protected=True)
        images_steps.delete_images([image_name], check=False)
        images_steps.close_notification('error')
        images_steps.check_image_present(image_name)
        images_steps.update_image(image_name, protected=False)

    @pytest.mark.idempotent_id('50dcf89e-370a-47d2-a0eb-c56dd77c968e',
                               any_one='admin')
    @pytest.mark.idempotent_id('8c85f869-993b-4447-98e4-fc1e4ebacb4e',
                               any_one='user')
    def test_edit_image(self, image, images_steps):
        """Verify that user can edit image."""
        new_image_name = image.name + '(updated)'
        with image.put(name=new_image_name):
            images_steps.update_image(image.name, new_image_name)

    @pytest.mark.idempotent_id('619298ae-f9f5-4afa-a50b-c3f5faa38c81',
                               any_one='admin')
    @pytest.mark.idempotent_id('f2bb54d2-f926-4c7c-85ce-2737e109000d',
                               any_one='user')
    def test_create_volume_from_image(self, image, images_steps,
                                      volumes_steps_ui):
        """Verify that user can create volume from image."""
        volume_name = next(utils.generate_ids())
        images_steps.create_volume(image.name, volume_name)
        volumes_steps_ui.check_volume_present(volume_name, timeout=90)
        volumes_steps_ui.delete_volume(volume_name)

    @pytest.mark.idempotent_id('3167e844-1d13-44d5-aa1e-85c58c086240',
                               any_one='admin')
    @pytest.mark.idempotent_id('db91fc36-89ce-49ed-95f5-34948cc70715',
                               any_one='user')
    def test_set_image_disk_and_ram_size(self, create_image, images_steps):
        """Verify that image limits has influence to flavor choice."""
        ram_size = 1024
        disk_size = 4

        image_name = next(utils.generate_ids(length=20))
        create_image(image_name, min_disk=disk_size, min_ram=ram_size)
        images_steps.check_flavors_limited_in_launch_instance_form(image_name,
                                                                   disk_size,
                                                                   ram_size)

    @pytest.mark.idempotent_id('f5339379-2e89-4adf-9074-78ed3c7e9a4e',
                               any_one='admin')
    @pytest.mark.idempotent_id('7187dbc4-6f56-4f5c-9e88-b61c3aed7b01',
                               any_one='user')
    def test_public_image_visibility(self, images_steps):
        """Verify that public image is visible for other users."""
        images_steps.check_public_image_visible('TestVM')

    @pytest.mark.idempotent_id('3c98d922-df89-4701-a4b1-c5258fda5d7b',
                               any_one='admin')
    @pytest.mark.idempotent_id('782940f1-f958-4275-b716-232a56fea743',
                               any_one='user')
    def test_launch_instance_from_image(self, image, images_steps,
                                        instances_steps):
        """Verify that user can launch instance from image."""
        instance_name = next(utils.generate_ids())
        images_steps.launch_instance(image.name, instance_name,
                                     network_name=config.INTERNAL_NETWORK_NAME)
        instances_steps.check_instance_active(instance_name)
        instances_steps.delete_instance(instance_name)

    @pytest.mark.idempotent_id('db36570f-c87e-4629-a83b-80eed6cbcab3',
                               any_one='admin')
    @pytest.mark.idempotent_id('e3ed0226-2e69-44bd-88ea-a7d9228111fe',
                               any_one='user')
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
        image_description = next(utils.generate_ids())
        images_steps.update_image(image.name, description=image_description)
        images_steps.check_image_info(image.name,
                                      expected_description=image_description)

    @pytest.mark.idempotent_id('c42d793b-efa9-46c4-b031-9f7bf7a49cd1',
                               any_one='admin')
    @pytest.mark.idempotent_id('796fcdf5-c258-4acc-8d93-786641615c48',
                               any_one='user')
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

    @pytest.mark.idempotent_id('e0aec971-00ea-41a4-9369-fc6ef3ea774d',
                               any_one='admin')
    @pytest.mark.idempotent_id('71c60320-d5d1-4e04-a3fd-1222f054d577',
                               any_one='user')
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

        metadata = {next(utils.generate_ids('metadata')):
                    next(utils.generate_ids("value"))
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
            image_names=utils.utils.generate_ids(length=20))[0]
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
        image_name = next(utils.utils.generate_ids(length=20))
        with utils.generate_file_context(
                postfix='.qcow2', size=config.BIG_FILE_SIZE) as file_path:
            create_image(image_name, image_file=file_path, big_image=True)
