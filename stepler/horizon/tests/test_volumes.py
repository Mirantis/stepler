"""
------------
Volume tests
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

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any user."""

    @pytest.mark.idempotent_id('4e0dd745-6654-4503-bc34-3cba858709fd',
                               any_one='admin')
    @pytest.mark.idempotent_id('bba8fd16-44e6-437a-9c10-c8ebf3414f4e',
                               any_one='user')
    def test_edit_volume(self, volume, volumes_steps_ui):
        """Verify that user can edit volume."""
        new_name = volume.name + ' (updated)'
        with volume.put(name=new_name):
            volumes_steps_ui.edit_volume(volume_name=volume.name,
                                         new_volume_name=new_name)

    @pytest.mark.idempotent_id('e4c1eab9-ddf4-4a75-915e-81e3886ac27b',
                               any_one='admin', volumes_count=1)
    @pytest.mark.idempotent_id('5f7f4fac-a19b-481a-9c61-18c1923cfa7d',
                               any_one='admin', volumes_count=2)
    @pytest.mark.idempotent_id('e71f4484-7c03-4dd9-a087-1217a86278a8',
                               any_one='user', volumes_count=1)
    @pytest.mark.idempotent_id('d4258de3-ab3c-4460-986e-e68e8801c43f',
                               any_one='user', volumes_count=2)
    @pytest.mark.parametrize('volumes_count', [1, 2])
    def test_delete_volumes(self, volumes_count, volumes_steps_ui,
                            create_volumes):
        """Verify that user can delete volumes as bunch."""
        volume_names = list(utils.generate_ids('volume', count=volumes_count))
        create_volumes(volume_names)

    @pytest.mark.idempotent_id('ff2319a8-5918-4821-ad69-8729a51e3d4e',
                               any_one='admin')
    @pytest.mark.idempotent_id('1a6f8444-4486-41aa-85f4-1dd41c62ff30',
                               any_one='user')
    def test_volumes_pagination(self, volumes_steps_ui, create_volumes,
                                update_settings):
        """Verify that volumes pagination works right and back."""
        volume_names = list(utils.generate_ids('volume', count=3))
        create_volumes(volume_names)
        update_settings(items_per_page=1)
        volumes_steps_ui.check_volumes_pagination(volume_names)

    @pytest.mark.idempotent_id('67ac61fb-63ec-4f83-a88a-553fb3b21a3c',
                               any_one='admin')
    @pytest.mark.idempotent_id('b08c7894-8a17-4f22-92c9-107dd8bf19f5',
                               any_one='user')
    def test_view_volume(self, volume, volumes_steps_ui):
        """Verify that user can view volume info."""
        volumes_steps_ui.view_volume(volume.name)

    @pytest.mark.idempotent_id('b3db692c-a132-4450-ba3b-6ab6c66c3846',
                               any_one='admin')
    @pytest.mark.idempotent_id('5329c92e-fc4b-4765-a608-cc659fabbb29',
                               any_one='user')
    def test_change_volume_type(self, create_volume, volumes_steps_ui):
        """Verify that user can change volume type."""
        volume_name = utils.generate_ids('volume').next()
        create_volume(volume_name, volume_type=None)
        volumes_steps_ui.change_volume_type(volume_name)

    @pytest.mark.idempotent_id('65272c3b-c2ea-42e6-91ac-f1daa43fdbfc',
                               any_one='admin')
    @pytest.mark.idempotent_id('a4ab8682-eed6-4d00-8975-4289e2aac4d3',
                               any_one='user')
    def test_upload_volume_to_image(self, volume, images_steps,
                                    volumes_steps_ui):
        """Verify that user can upload volume to image."""
        image_name = next(utils.generate_ids(length=20))
        volumes_steps_ui.upload_volume_to_image(volume.name, image_name)
        images_steps.check_image_present(image_name, timeout=30)
        images_steps.delete_image(image_name)

    @pytest.mark.idempotent_id('e343b260-b840-4345-ab19-8dabee3478c7',
                               any_one='admin')
    @pytest.mark.idempotent_id('eaa7d1e6-15ca-4fbc-b3cd-f0959e39ff54',
                               any_one='user')
    def test_volume_extend(self, volume, volumes_steps_ui):
        """Verify that user can extend volume size."""
        volumes_steps_ui.extend_volume(volume.name)

    @pytest.mark.idempotent_id('0374870e-5d84-4574-a114-cf78db640c26',
                               any_one='admin')
    @pytest.mark.idempotent_id('439e8ca5-0d87-49aa-9458-a239fa6ff1e1',
                               any_one='user')
    def test_launch_volume_as_instance(self, volume, instances_steps,
                                       volumes_steps_ui):
        """Verify that admin can launch volume as instance."""
        instance_name = next(utils.generate_ids('instance'))
        volumes_steps_ui.launch_volume_as_instance(
            volume.name, instance_name,
            network_name=config.INTERNAL_NETWORK_NAME)
        instances_steps.check_instance_active(instance_name)
        instances_steps.delete_instance(instance_name)

    @pytest.mark.idempotent_id('cdb362e0-4447-4f89-9af2-5e6f0e80e859',
                               any_one='admin')
    @pytest.mark.idempotent_id('fb043d55-47e5-48fb-8ae0-c4bc860742a8',
                               any_one='user')
    def test_create_volume_with_description(self, create_volume):
        """**Scenario:** Create volume with description.

        **Steps:**

        #. Create volume with description
        #. Check that volume created
        #. Check that description is correct

        **Teardown:**

        #. Delete volume
        """
        volume_name = next(utils.generate_ids('volume'))
        volume_description = next(utils.generate_ids('volume_description'))
        create_volume(volume_name, description=volume_description)

    @pytest.mark.idempotent_id('4e019917-e519-4fbd-956d-5b5df83a5de1',
                               any_one='admin')
    @pytest.mark.idempotent_id('e2548571-e376-44e9-a6db-9f533b5d7c81',
                               any_one='user')
    def test_create_bigger_volume_from_volume(self, volume, create_volume):
        """**Scenario:** Create bigger volume from another volume.

        **Steps:**

        #. Create volume with 1GB size
        #. Create volume from created volume with 2GB size
        #. Check that volume is created

        **Teardown:**

        #. Delete volumes
        """
        volume_name = next(utils.generate_ids('volume'))
        create_volume(volume_name,
                      source_type=config.VOLUME_SOURCE,
                      source_name=volume.name,
                      volume_type=None,
                      volume_size=2)


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('1a8ee83f-e741-462c-af4f-e15b233daca4')
    def test_change_volume_status(self, volume, volumes_steps_ui):
        """Verify that admin can change volume status."""
        volumes_steps_ui.change_volume_status(volume.name, 'Error')
        volumes_steps_ui.change_volume_status(volume.name, 'Available')

    @pytest.mark.idempotent_id('371badd3-a2f7-484d-9fdb-9ad06d431623')
    def test_manage_volume_attachments(self, volume, instance,
                                       volumes_steps_ui):
        """Verify that admin can manage volume attachments."""
        volumes_steps_ui.attach_instance(volume.name, instance.name)
        volumes_steps_ui.detach_instance(volume.name, instance.name)

    @pytest.mark.idempotent_id('32b295cd-fbd0-44c1-b7b9-175f5ad7434c')
    def test_transfer_volume(self, volume, auth_steps, volumes_steps_ui):
        """Verify that volume can be transfered between users."""
        transfer_name = next(utils.generate_ids('transfer'))
        transfer_id, transfer_key = volumes_steps_ui.create_transfer(
            volume.name, transfer_name)
        auth_steps.logout()
        auth_steps.login(config.USER_NAME, config.USER_PASSWD)
        volumes_steps_ui.accept_transfer(transfer_id, transfer_key,
                                         volume.name)

    @pytest.mark.idempotent_id('e585242-9443-4e78-a7fe-3ee6097459bb')
    @pytest.mark.requires('cinder_nodes_count >= 2')
    def test_migrate_volume(self, volume, volumes_steps_ui):
        """Verify that admin can migrate volume between available hosts."""
        old_host, _ = volumes_steps_ui.migrate_volume(volume.name)
        volumes_steps_ui.migrate_volume(volume.name, old_host)
