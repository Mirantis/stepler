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

    @pytest.mark.idempotent_id(
        'a54b457e-f3b2-4903-9702-b9e75ede5830',
        any_one='admin',
        horizon_images={'count': 1})
    @pytest.mark.idempotent_id(
        '6094e9bf-67dd-4f19-a0a3-73cf7b91603a',
        any_one='admin',
        horizon_images={'count': 2})
    @pytest.mark.idempotent_id(
        '083edf5e-ba16-414a-854d-d0ddcbbe7186',
        any_one='user',
        horizon_images={'count': 1})
    @pytest.mark.idempotent_id(
        'ace4a999-9318-4446-a957-57143e52703d',
        any_one='user',
        horizon_images={'count': 2})
    @pytest.mark.parametrize(
        'horizon_images', [{'count': 1}, {'count': 2}], ids=['1', '2'],
        indirect=True)
    def test_delete_images(self, horizon_images, images_steps_ui):
        """**Scenario:** Verify that user can delete images as bunch.

        **Setup:**

        #. Create images using API

        **Steps:**

        #. Delete images as bunch using UI
        """
        images_steps_ui.delete_images([image.name for image in horizon_images])

    @pytest.mark.idempotent_id('c4cf3c6d-45d2-4629-b9fe-3e8eed3f1e59',
                               any_one='admin')
    @pytest.mark.idempotent_id('a7330cae-30ea-4131-a819-42a71f87576d',
                               any_one='user')
    def test_view_image(self, horizon_image, images_steps_ui):
        """**Scenario:** Verify that user can view image info.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. View image using UI

        **Teardown:**

        #. Delete image using API
        """
        images_steps_ui.view_image(horizon_image.name)

    @pytest.mark.idempotent_id('b39a1540-f500-4f86-b123-e89262a51670',
                               any_one='admin')
    @pytest.mark.idempotent_id('2454c803-bc07-44c7-b842-0151c510c7d2',
                               any_one='user')
    @pytest.mark.parametrize('horizon_images', [{'count': 3}], ids=[''],
                             indirect=True)
    def test_images_pagination(self,
                               glance_steps,
                               horizon_images,
                               update_settings,
                               images_steps_ui):
        """**Scenario:** Verify images pagination works right and back.

        **Setup:**

        #. Create images using API

        **Steps:**

        #. Update ``items_per_page`` parameter to 1 using UI
        #. Check images pagination using UI

        **Teardown:**

        #. Delete images using API
        """
        image_names = [image.name for image in glance_steps.get_images()]
        update_settings(items_per_page=1)
        images_steps_ui.check_images_pagination(image_names)

    @pytest.mark.idempotent_id('b835ce2b-41b2-4d7a-8b8f-139163234852',
                               any_one='admin')
    @pytest.mark.idempotent_id('1b439ae8-32aa-476d-abf9-3e2ae796de46',
                               any_one='user')
    def test_update_image_metadata(self, horizon_image, images_steps_ui):
        """**Scenario:** Verify that user can update image metadata.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. Update image metadata using UI
        #. Check metadata has been updated

        **Teardown:**

        #. Delete image using API
        """
        metadata = {next(utils.generate_ids('metadata')):
                    next(utils.generate_ids("value"))
                    for _ in range(2)}
        images_steps_ui.add_metadata(horizon_image.name, metadata)

    @pytest.mark.idempotent_id('4016e9af-257b-4df2-8c63-5716f134e5bb',
                               any_one='admin')
    @pytest.mark.idempotent_id('637b39da-5648-4d46-bf3f-d51ca858928f',
                               any_one='user')
    def test_remove_protected_image(self, horizon_image, images_steps_ui):
        """**Scenario:** Verify that user can't delete protected image.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. Make image protected using UI
        #. Try to delete image using UI
        #. Close error notification
        #. Check that image is present
        #. Make image public using UI

        **Teardown:**

        #. Delete image using API
        """
        images_steps_ui.update_image(horizon_image.name, protected=True)
        images_steps_ui.delete_images([horizon_image.name], check=False)
        images_steps_ui.close_notification('error')
        images_steps_ui.check_image_present(horizon_image.name)
        images_steps_ui.update_image(horizon_image.name, protected=False)

    @pytest.mark.idempotent_id('50dcf89e-370a-47d2-a0eb-c56dd77c968e',
                               any_one='admin')
    @pytest.mark.idempotent_id('8c85f869-993b-4447-98e4-fc1e4ebacb4e',
                               any_one='user')
    def test_edit_image(self, horizon_image, images_steps_ui):
        """**Scenario:** Verify that user can edit image.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. Edit image name using UI

        **Teardown:**

        #. Delete image using API
        """
        new_image_name = horizon_image.name + '(updated)'
        images_steps_ui.update_image(horizon_image.name, new_image_name)

    @pytest.mark.idempotent_id('619298ae-f9f5-4afa-a50b-c3f5faa38c81',
                               any_one='admin')
    @pytest.mark.idempotent_id('f2bb54d2-f926-4c7c-85ce-2737e109000d',
                               any_one='user')
    def test_create_volume_from_image(self, horizon_image, images_steps_ui,
                                      volumes_steps_ui):
        """**Scenario:** Verify that user can create volume from image.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. Create volume from image using UI
        #. Check that volume is present
        #. Delete volume using UI

        **Teardown:**

        #. Delete image using API
        """
        volume_name = next(utils.generate_ids())
        images_steps_ui.create_volume(horizon_image.name, volume_name)
        volumes_steps_ui.check_volume_present(volume_name, timeout=90)
        volumes_steps_ui.delete_volume(volume_name)

    @pytest.mark.idempotent_id('3167e844-1d13-44d5-aa1e-85c58c086240',
                               any_one='admin')
    @pytest.mark.idempotent_id('db91fc36-89ce-49ed-95f5-34948cc70715',
                               any_one='user')
    def test_set_image_disk_and_ram_size(self, images_steps_ui):
        """**Scenario:** Image limits has influence on flavor choice.

        **Steps:**

        #. Create image with min disk and min ram using UI
        #. Check that image limits has influence on flavor choice using UI

        **Teardown:**

        #. Delete image using API
        """
        ram_size = 1024
        disk_size = 4

        image_name = next(utils.generate_ids(length=20))
        images_steps_ui.create_image(image_name,
                                     min_disk=disk_size,
                                     min_ram=ram_size)
        images_steps_ui.check_flavors_limited_in_launch_instance_form(
            image_name, disk_size, ram_size)

    @pytest.mark.idempotent_id('f5339379-2e89-4adf-9074-78ed3c7e9a4e',
                               any_one='admin')
    @pytest.mark.idempotent_id('7187dbc4-6f56-4f5c-9e88-b61c3aed7b01',
                               any_one='user')
    def test_public_image_visibility(self, images_steps_ui):
        """**Scenario:** Verify that public image is visible for other users.

        **Steps:**

        #. Check that public image is visible for different users using UI
        """
        images_steps_ui.check_public_image_visible(
            config.HORIZON_TEST_IMAGE_CIRROS)

    @pytest.mark.idempotent_id('3c98d922-df89-4701-a4b1-c5258fda5d7b',
                               any_one='admin')
    @pytest.mark.idempotent_id('782940f1-f958-4275-b716-232a56fea743',
                               any_one='user')
    def test_launch_instance_from_image(self, horizon_image, images_steps_ui,
                                        instances_steps_ui):
        """**Scenario:** Verify that user can launch instance from image.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. Launch instance from image using UI
        #. Check that instance is present
        #. Delete instance using UI

        **Teardown:**

        #. Delete image using API
        """
        instance_name = next(utils.generate_ids())
        images_steps_ui.launch_instance(
            horizon_image.name,
            instance_name,
            network_name=config.INTERNAL_NETWORK_NAME,
            flavor=config.HORIZON_TEST_FLAVOR_TINY)
        instances_steps_ui.check_instance_active(instance_name)
        instances_steps_ui.delete_instance(instance_name)

    @pytest.mark.idempotent_id('db36570f-c87e-4629-a83b-80eed6cbcab3',
                               any_one='admin')
    @pytest.mark.idempotent_id('e3ed0226-2e69-44bd-88ea-a7d9228111fe',
                               any_one='user')
    def test_edit_image_description(self, horizon_image, images_steps_ui):
        """**Scenario:** Check addition of image description.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. Click on image and check that description is missing
        #. Edit image by adding description using UI
        #. Click on image and check description in detailed info

        **Teardown:**

        #. Delete image using API
        """
        images_steps_ui.check_image_info(horizon_image.name,
                                         expected_description=None)

        image_description = next(utils.generate_ids())
        images_steps_ui.update_image(horizon_image.name,
                                     description=image_description)
        images_steps_ui.check_image_info(
            horizon_image.name, expected_description=image_description)

    @pytest.mark.idempotent_id('c42d793b-efa9-46c4-b031-9f7bf7a49cd1',
                               any_one='admin')
    @pytest.mark.idempotent_id('796fcdf5-c258-4acc-8d93-786641615c48',
                               any_one='user')
    def test_edit_image_disk_and_ram(self, horizon_image, images_steps_ui):
        """**Scenario:** Check edition of minimum disk and RAM.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. Edit image and set Minimum Disk = 60Gb and Minimum RAM = 0
        #. Try to launch instance
        #. Check that all flavors with disk < 60Gb are unavailable
        #. Edit image and set Minimum Disk = 0Gb and Minimum RAM = 4096Mb
        #. Try to launch instance
        #. Check that all flavors with ram < 4096Mb are unavailable

        **Teardown:**

        #. Delete image using API
        """
        for min_disk, min_ram in [(60, 0), (0, 4096)]:
            images_steps_ui.update_image(horizon_image.name,
                                         min_disk=min_disk,
                                         min_ram=min_ram)
            images_steps_ui.check_flavors_limited_in_launch_instance_form(
                horizon_image.name, min_disk, min_ram)

    @pytest.mark.idempotent_id('e0aec971-00ea-41a4-9369-fc6ef3ea774d',
                               any_one='admin')
    @pytest.mark.idempotent_id('71c60320-d5d1-4e04-a3fd-1222f054d577',
                               any_one='user')
    def test_add_delete_image_metadata(self, horizon_image, images_steps_ui):
        """**Scenario:** Check addition and deletion of image metadata.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. Check that no metadata in Custom properties
        #. Add metadata using UI
        #. Check that metadata appeared in Custom properties and values are
           correct
        #. Delete metadata using UI
        #. Check that metadata disappeared in Custom properties

        **Teardown:**

        #. Delete image using API
        """
        images_steps_ui.check_image_info(horizon_image.name,
                                         expected_metadata=None)

        metadata = {next(utils.generate_ids('metadata')):
                    next(utils.generate_ids("value"))
                    for _ in range(2)}
        images_steps_ui.add_metadata(horizon_image.name, metadata)
        images_steps_ui.check_image_info(horizon_image.name,
                                         expected_metadata=metadata)

        images_steps_ui.delete_metadata(horizon_image.name, metadata)
        images_steps_ui.check_image_info(horizon_image.name,
                                         expected_metadata=None)

    @pytest.mark.idempotent_id('4262e99a-10c5-4ce5-b48a-160568611bb0',
                               any_one='admin')
    @pytest.mark.idempotent_id('dc5e9a46-cd20-47f7-bd84-739563864af2',
                               any_one='user')
    def test_open_image_info_in_new_tab(self, horizon_image, images_steps_ui):
        """**Scenario:** Check opening image info in new tab works.

        **Setup:**

        #. Create image using API

        **Steps:**

        #. Open image info in new tab

        **Teardown:**

        #. Delete image using API
        """
        images_steps_ui.open_image_info_in_new_tab(horizon_image.name)


@pytest.mark.usefixtures('user_only')
class TestUserOnly(object):
    """Tests for user only."""

    @pytest.mark.idempotent_id('451ea18f-e513-48ac-999a-4e719516478e')
    def test_image_privacy(self, glance_steps, images_steps_ui):
        """**Scenario:** Non public image is not visible for other users.

        **Setup:**

        #. Login as user to another project

        **Steps:**

        #. Create image with public=False as admin using API
        #. Check that image is not available as public image using UI

        **Teardown:**

        #. Delete image using API
        """
        image = glance_steps.create_images(
            utils.get_file_path(config.CIRROS_QCOW2_URL),
            image_names=utils.generate_ids(length=20))[0]
        images_steps_ui.check_non_public_image_not_visible(image.name)

    # the following test is executed only for one user because of its long
    # duration (> 1 hour)
    # TODO(ssokolov) add some mark for specific environment and execution time
    @pytest.mark.idempotent_id('b846cf53-d3fa-4cca-8b10-fbaf50749f7c')
    def test_big_image_create_delete(self, images_steps_ui):
        """**Scenario:** Check big image creation and deletion from file.

        **Steps:**

        #. Create file 100Gb
        #. Create image from this file using UI

        **Teardown:**

        #. Delete big file
        #. Delete image using API
        """
        image_name = next(utils.generate_ids(length=20))
        with utils.generate_file_context(
                postfix='.qcow2', size=config.BIG_FILE_SIZE) as file_path:
            images_steps_ui.create_image(image_name,
                                         image_file=file_path,
                                         big_image=True)
