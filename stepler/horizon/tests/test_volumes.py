"""
------------
Volume tests
------------

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

import pytest

from stepler.horizon.config import (INTERNAL_NETWORK_NAME,
                                    USER_NAME,
                                    USER_PASSWD)
from stepler.horizon.utils import generate_ids


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any user."""

    def test_edit_volume(self, volume, volumes_steps):
        """Verify that user can edit volume."""
        new_name = volume.name + ' (updated)'
        with volume.put(name=new_name):
            volumes_steps.edit_volume(volume_name=volume.name,
                                      new_volume_name=new_name)

    @pytest.mark.parametrize('volumes_count', [1, 2])
    def test_delete_volumes(self, volumes_count, volumes_steps,
                            create_volumes):
        """Verify that user can delete volumes as bunch."""
        volume_names = list(generate_ids('volume', count=volumes_count))
        create_volumes(volume_names)

    def test_volumes_pagination(self, volumes_steps, create_volumes,
                                update_settings):
        """Verify that volumes pagination works right and back."""
        volume_names = list(generate_ids('volume', count=3))
        create_volumes(volume_names)
        update_settings(items_per_page=1)

        tab_volumes = volumes_steps.tab_volumes()

        tab_volumes.table_volumes.row(
            name=volume_names[2]).wait_for_presence(30)
        assert tab_volumes.table_volumes.link_next.is_present
        assert not tab_volumes.table_volumes.link_prev.is_present

        tab_volumes.table_volumes.link_next.click()

        tab_volumes.table_volumes.row(
            name=volume_names[1]).wait_for_presence(30)
        assert tab_volumes.table_volumes.link_next.is_present
        assert tab_volumes.table_volumes.link_prev.is_present

        tab_volumes.table_volumes.link_next.click()

        tab_volumes.table_volumes.row(
            name=volume_names[0]).wait_for_presence(30)
        assert not tab_volumes.table_volumes.link_next.is_present
        assert tab_volumes.table_volumes.link_prev.is_present

        tab_volumes.table_volumes.link_prev.click()

        tab_volumes.table_volumes.row(
            name=volume_names[1]).wait_for_presence(30)
        assert tab_volumes.table_volumes.link_next.is_present
        assert tab_volumes.table_volumes.link_prev.is_present

        tab_volumes.table_volumes.link_prev.click()

        tab_volumes.table_volumes.row(
            name=volume_names[2]).wait_for_presence(30)
        assert tab_volumes.table_volumes.link_next.is_present
        assert not tab_volumes.table_volumes.link_prev.is_present

    def test_view_volume(self, volume, volumes_steps):
        """Verify that user can view volume info."""
        volumes_steps.view_volume(volume.name)

    def test_change_volume_type(self, create_volume, volumes_steps):
        """Verify that user can change volume type."""
        volume_name = generate_ids('volume').next()
        create_volume(volume_name, volume_type=None)
        volumes_steps.change_volume_type(volume_name)

    def test_upload_volume_to_image(self, volume, images_steps, volumes_steps):
        """Verify that user can upload volume to image."""
        image_name = next(generate_ids('image', length=20))
        volumes_steps.upload_volume_to_image(volume.name, image_name)

        images_steps.page_images().table_images.row(
            name=image_name).wait_for_presence(30)
        images_steps.delete_image(image_name)

    def test_volume_extend(self, volume, volumes_steps):
        """Verify that user can extend volume size."""
        volumes_steps.extend_volume(volume.name)

    def test_launch_volume_as_instance(self, volume, instances_steps,
                                       volumes_steps):
        """Verify that admin can launch volume as instance."""
        instance_name = next(generate_ids('instance'))
        volumes_steps.launch_volume_as_instance(
            volume.name, instance_name, network_name=INTERNAL_NETWORK_NAME)

        instances_steps.page_instances().table_instances.row(
            name=instance_name).wait_for_status('Active')
        instances_steps.delete_instance(instance_name)


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    def test_change_volume_status(self, volume, volumes_steps):
        """Verify that admin can change volume status."""
        volumes_steps.change_volume_status(volume.name, 'Error')
        volumes_steps.change_volume_status(volume.name, 'Available')

    def test_manage_volume_attachments(self, volume, instance, volumes_steps):
        """Verify that admin can manage volume attachments."""
        volumes_steps.attach_instance(volume.name, instance.name)
        volumes_steps.detach_instance(volume.name, instance.name)

    def test_transfer_volume(self, volume, auth_steps, volumes_steps):
        """Verify that volume can be transfered between users."""
        transfer_name = next(generate_ids('transfer'))
        transfer_id, transfer_key = volumes_steps.create_transfer(
            volume.name, transfer_name)
        auth_steps.logout()
        auth_steps.login(USER_NAME, USER_PASSWD)
        volumes_steps.accept_transfer(transfer_id, transfer_key, volume.name)

    def test_migrate_volume(self, volume, volumes_steps):
        """Verify that admin can migrate volume between available hosts."""
        old_host, _ = volumes_steps.migrate_volume(volume.name)
        volumes_steps.migrate_volume(volume.name, old_host)
