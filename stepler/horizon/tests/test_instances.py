"""
--------------
Instance tests
--------------
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


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for anyone."""

    @pytest.mark.smoke
    @pytest.mark.idempotent_id('54a6c9d9-09c8-4f74-a670-b1c0d4bb1d74',
                               any_one='admin')
    @pytest.mark.idempotent_id('a3cd86a4-70c4-4a3e-b9b6-d9774d8aeae3',
                               any_one='user')
    def test_create_instance(self, instances_steps_ui):
        """**Scenario:** Verify that user can create and delete instance.

        **Steps:**

        #. Create server using UI
        #. Delete server using UI
        """
        instance_name = instances_steps_ui.create_instance(
            network_name=config.INTERNAL_NETWORK_NAME)[0]
        instances_steps_ui.delete_instance(instance_name)

    @pytest.mark.smoke
    @pytest.mark.idempotent_id('53c038f0-b63c-461c-983b-7db82fd0d626',
                               any_one='admin', horizon_servers=2)
    @pytest.mark.idempotent_id('ecb6230a-3062-46af-af06-4f9208ae2961',
                               any_one='admin', horizon_servers=1)
    @pytest.mark.idempotent_id('acf99c3a-c22c-4e33-a58e-58a49d94877f',
                               any_one='user', horizon_servers=2)
    @pytest.mark.idempotent_id('bf0ea67b-fe0a-4be3-bc83-e9ca8ba0b3e2',
                               any_one='user', horizon_servers=1)
    @pytest.mark.parametrize('horizon_servers', [2, 1], indirect=True)
    def test_delete_instances(self, horizon_servers, instances_steps_ui):
        """**Scenario:** Verify that user can delete instances as bunch.

        **Setup:**

        #. Create servers using API

        **Steps:**

        #. Delete servers as bunch using UI
        """
        server_names = [server.name for server in horizon_servers]
        instances_steps_ui.delete_instances(server_names)

    @pytest.mark.idempotent_id('005870b0-73fd-4c56-a6ec-8c4bad46f058',
                               any_one='admin')
    @pytest.mark.idempotent_id('e534aeb2-b0d4-407c-9f89-64a5c0739513',
                               any_one='user')
    def test_lock_instance(self, horizon_server, instances_steps_ui):
        """**Scenario:** Verify that user can lock instance.

        **Setup:**

        #. Create server using API

        **Steps:**

        #. Lock server using UI
        #. Unlock server using UI

        **Teardown:**

        #. Delete server using API
        """
        instances_steps_ui.lock_instance(horizon_server.name)
        instances_steps_ui.unlock_instance(horizon_server.name)

    @pytest.mark.idempotent_id('6a01661b-c7af-47ad-9aaa-8b185dda8d3c',
                               any_one='admin')
    @pytest.mark.idempotent_id('48649a7b-6496-4ff9-9041-dcb52f1324f3',
                               any_one='user')
    def test_view_instance(self, horizon_server, instances_steps_ui):
        """**Scenario:** Verify that user can view instance details.

        **Setup:**

        #. Create server using API

        **Steps:**

        #. View server using UI

        **Teardown:**

        #. Delete server using API
        """
        instances_steps_ui.view_instance(horizon_server.name)

    @pytest.mark.idempotent_id('8867776e-ff19-49a7-8d10-ea78cc02cfc6',
                               any_one='admin')
    @pytest.mark.idempotent_id('de45feb0-85bb-4b54-b8dc-0ead39620bfa',
                               any_one='user')
    @pytest.mark.parametrize('horizon_servers', [3], ids=[''], indirect=True)
    def test_instances_pagination(self,
                                  server_steps,
                                  horizon_servers,
                                  update_settings,
                                  instances_steps_ui):
        """**Scenario:** Verify that instances pagination works.

        **Setup:**

        #. Create 3 servers using API

        **Steps:**

        #. Check sum of instances
        #. Update ``items_per_page`` parameter to 1 using UI
        #. Check instances pagination using UI

        **Teardown:**

        #. Delete 3 servers using API
        """
        instance_names = [instance.name
                          for instance in server_steps.get_servers()]
        instances_steps_ui.check_instances_sum(instance_names)
        update_settings(items_per_page=1)
        instances_steps_ui.check_instances_pagination(instance_names)

    @pytest.mark.idempotent_id('060136f-d477-4177-a387-8e8d01ec4ecd',
                               any_one='admin')
    @pytest.mark.idempotent_id('edc5f03d-ea66-4dae-8322-7cd679c2d829',
                               any_one='user')
    @pytest.mark.parametrize('horizon_servers', [2], ids=[''], indirect=True)
    def test_filter_instances(self, horizon_servers, instances_steps_ui):
        """**Scenario:** Verify that user can filter instances.

        **Setup:**

        #. Create servers using API

        **Steps:**

        #. Filter servers using UI
        #. Reset filter using UI

        **Teardown:**

        #. Delete servers using API
        """
        instances_steps_ui.filter_instances(query=horizon_servers[0].name)
        instances_steps_ui.reset_instances_filter()

    @pytest.mark.smoke
    @pytest.mark.idempotent_id('d6fc41ea-3a05-11e7-a867-ab2bfc1dfe61',
                               any_one='admin')
    @pytest.mark.idempotent_id('df175266-3a05-11e7-9adf-2ba1863bd2b4',
                               any_one='user')
    def test_nova_associate_ip(self,
                               horizon_server,
                               floating_ip,
                               instances_steps_ui):
        """**Scenario:** Verify associate/disassociate ip to instance.

        **Setup:**

        #. Create server using API
        #. Create floating IP using API

        **Steps:**

        #. Associate floating ip to instance
        #. Disassociate floating ip from instance

        **Teardown:**

        #. Delete server using API
        #. Delete floating IP using API
        """
        instances_steps_ui.nova_associate_floating_ip(
            horizon_server.name,
            floating_ip.ip)
        instances_steps_ui.nova_disassociate_floating_ip(
            horizon_server.name)

    @pytest.mark.idempotent_id('886b9820-3ef4-11e7-b7fb-938b7d064835',
                               any_one='admin')
    @pytest.mark.idempotent_id('89e672f6-3ef4-11e7-95a1-b7df5a42063f',
                               any_one='user')
    def test_create_instance_snapshot(self, horizon_server,
                                      instances_steps_ui,
                                      images_steps_ui):
        """**Scenario:** Verify that user can create instance snapshot.

        **Setup:**

        #. Create server using API

        **Steps:**

        #. Create snapshot
        #. Check that snapshot created
        #. Delete snapshot

        **Teardown:**

        #. Delete server using API
        """
        snapshot_name = instances_steps_ui.create_instance_snapshot(
            horizon_server.name)
        images_steps_ui.check_image_present(snapshot_name)
        images_steps_ui.delete_image(snapshot_name)

    @pytest.mark.idempotent_id('8523aad8-4082-11e7-aed3-1bd4f24c633d',
                               any_one='admin')
    @pytest.mark.idempotent_id('85d5d17c-4082-11e7-9efb-17e239f72067',
                               any_one='user')
    def test_resize_instance(self, horizon_server,
                             instances_steps_ui):
        """**Scenario:** Verify that user can resize instance.

        **Setup:**

        #. Create server using API

        **Steps:**

        #. Resize instance

        **Teardown:**

        #. Delete server using API
        """
        instances_steps_ui.resize_instance(horizon_server.name)

    @pytest.mark.smoke
    @pytest.mark.idempotent_id('3387fea8-412d-11e7-bdbd-af7548dce310',
                               any_one='admin')
    @pytest.mark.idempotent_id('343d7576-412d-11e7-bd85-4fc37a08201a',
                               any_one='user')
    def test_edit_instance_name(self, horizon_server,
                                instances_steps_ui):
        """**Scenario:** Verify that user can edit instance name.

        **Setup:**

        #. Create server using API

        **Steps:**

        #. Rename instance

        **Teardown:**

        #. Delete server using API
        """
        instances_steps_ui.rename_instance(horizon_server.name)

    @pytest.mark.smoke
    @pytest.mark.idempotent_id('c5ecd044-450f-11e7-b588-23782e95bb3c',
                               any_one='admin')
    @pytest.mark.idempotent_id('c684af86-450f-11e7-8637-4b94848b5a9f',
                               any_one='user')
    def test_edit_instance_security_group(self, horizon_security_group,
                                          horizon_server,
                                          instances_steps_ui):
        """**Scenario:** Verify that user can edit instance security group.

        **Setup:**

        #. Create server using API

        **Steps:**

        #. Add security group to instance

        **Teardown:**

        #. Delete server using API
        """
        instances_steps_ui.add_security_group(
            horizon_server.name,
            horizon_security_group['name'])

    @pytest.mark.idempotent_id('68f1fbae-4cf2-11e7-b7fc-57cd3087863f',
                               any_one='admin')
    @pytest.mark.idempotent_id('74a1d870-4cf2-11e7-9757-57cda13b370c',
                               any_one='user')
    @pytest.mark.parametrize('horizon_servers', [3], ids=[''], indirect=True)
    def test_instances_pagination_filter(self,
                                         server_steps,
                                         horizon_servers,
                                         update_settings,
                                         instances_steps_ui):
        """**Scenario:** Verify that instances pagination work with filter.

        **Setup:**

        #. Create 3 servers using API

        **Steps:**

        #. Update ``items_per_page`` parameter to 1 using UI
        #. Check instances pagination with filtering using UI

        **Teardown:**

        #. Delete 3 servers using API
        """
        instance_names = [instance.name
                          for instance in server_steps.get_servers()]
        update_settings(items_per_page=1)
        instances_steps_ui.check_instances_pagination_filter(instance_names)


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('7140e6f0-45de-11e7-b72d-f3dd1dc0afb3')
    @pytest.mark.parametrize('horizon_servers', [3], ids=[''], indirect=True)
    def test_admin_instances_pagination(self,
                                        server_steps,
                                        horizon_servers,
                                        update_settings,
                                        instances_steps_ui):
        """**Scenario:** Verify that instances pagination work for admin.

        **Setup:**

        #. Create 3 servers using API

        **Steps:**

        #. Check sum of instances
        #. Update ``items_per_page`` parameter to 1 using UI as admin
        #. Check instances pagination using UI as admin

        **Teardown:**

        #. Delete 3 servers using API
        """
        instance_names = [instance.name
                          for instance in server_steps.get_servers()]
        instances_steps_ui.check_instances_sum(instance_names)
        update_settings(items_per_page=1)
        instances_steps_ui.check_admin_instances_pagination(instance_names)

    @pytest.mark.idempotent_id('55360490-4cc3-11e7-8097-2f3481188dc2')
    @pytest.mark.parametrize('horizon_servers', [2], ids=[''], indirect=True)
    def test_admin_filter_instances(self, horizon_servers, instances_steps_ui):
        """**Scenario:** Verify that user can filter instances as admin.

        **Setup:**

        #. Create two servers using API

        **Steps:**

        #. Filter servers using UI as admin
        #. Reset filter using UI as admin

        **Teardown:**

        #. Delete two servers using API
        """
        instances_steps_ui.admin_filter_instances(
            query=horizon_servers[0].name)
        instances_steps_ui.admin_reset_instances_filter()

    @pytest.mark.idempotent_id('4113a5cc-500a-11e7-a057-271f50a70c20')
    @pytest.mark.parametrize('horizon_servers', [3], ids=[''], indirect=True)
    def test_admin_instances_pagination_filter(self,
                                               server_steps,
                                               horizon_servers,
                                               update_settings,
                                               instances_steps_ui):
        """**Scenario:** Verify that instances pagination work with filter for admin.

        **Setup:**

        #. Create 3 servers using API

        **Steps:**

        #. Update ``items_per_page`` parameter to 1 using UI as admin
        #. Check instances pagination with filtering using UI as admin

        **Teardown:**

        #. Delete 3 servers using API
        """
        instance_names = [instance.name
                          for instance in server_steps.get_servers()]
        update_settings(items_per_page=1)
        instances_steps_ui.check_admin_instances_pagination_filter(
            instance_names)

    @pytest.mark.idempotent_id('da7150fc-4ce5-11e7-bf78-c712da53935b')
    def test_admin_delete_instance(self, horizon_server,
                                   instances_steps_ui):
        """**Scenario:** Verify that user can delete instance as admin.

        **Setup:**

        #. Create server using API

        **Steps:**

        #. Delete server using UI as admin
        """
        instances_steps_ui.admin_delete_instance(horizon_server.name)

    @pytest.mark.idempotent_id('20d68874-4ce5-11e7-8c5a-c3a2b1dcfe6f')
    @pytest.mark.parametrize('horizon_servers', [3], indirect=True)
    def test_admin_delete_instances(self, horizon_servers, instances_steps_ui):
        """**Scenario:** Verify that user can delete instances as bunch as admin.

        **Setup:**

        #. Create 3 servers using API

        **Steps:**

        #. Delete servers as bunch using UI as admin
        """
        server_names = [server.name for server in horizon_servers]
        instances_steps_ui.admin_delete_instances(server_names)

    @pytest.mark.idempotent_id('bdaebd08-e7e5-46c1-ae59-7b42df05146a')
    def test_launch_instances_together(self, instances_steps_ui,
                                       update_defaults):
        """**Scenario:** Verify that user can create 20 instances together.

        **Steps:**

        #. Set quotas to be able to run 50 servers
        #. Launch 5 servers at the same time
        #. Delete 5 servers as bunch

        **Teardown:**

        #. Restore original value for instances parameter
        """
        update_defaults({'instances': 50})
        instance_names = instances_steps_ui.create_instance(
            network_name=config.INTERNAL_NETWORK_NAME, count=5)
        instances_steps_ui.delete_instances(instance_names)

    @pytest.mark.idempotent_id('cb6d2044-5b37-11e7-bfb3-5404a69126b9')
    def test_suspend_instance(self, instances_steps_ui, server):
        """**Scenario:** Verify that instance was suspended.

        **Setup:**

        #. Create server using API

        **Steps:**

        #. Check instance suspend
        """
        instances_steps_ui.check_instance_suspend(instance_name=server.name)

    @pytest.mark.idempotent_id('ddab389e-5bf6-11e7-bfb3-5404a69126b9')
    def test_pause_instance(self, instances_steps_ui, server):
        """**Scenario:** Verify that instance was paused.

        **Setup:**

        #. Create server using API

        **Steps:**

        #. Check instance pause
        """
        instances_steps_ui.check_instance_pause(instance_name=server.name)
