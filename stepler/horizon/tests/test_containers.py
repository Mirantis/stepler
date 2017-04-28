"""
---------------
Container tests
---------------
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

from stepler.third_party import utils


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any one."""

    @pytest.mark.idempotent_id('e2804b4e-743e-4632-9c63-34066491a418',
                               any_one='admin')
    @pytest.mark.idempotent_id('31502fae-2fbb-4d69-9699-22ddb6983503',
                               any_one='user')
    def test_create_public_container(self, create_container_ui):
        """**Scenario:** Verify that one can create public container.

        **Steps:**

        #. Create public container using UI

        **Teardown:**

        #. Delete container using UI
        """
        container_name = next(utils.generate_ids('container'))
        create_container_ui(container_name, public=True)

    @pytest.mark.idempotent_id('fde52ec8-1e68-4c9d-86d3-6dbc5d915c85',
                               any_one='admin')
    @pytest.mark.idempotent_id('99c09de0-a6c6-4dad-b216-f758841b0598',
                               any_one='user')
    def test_available_public_container_url(self, create_container_ui,
                                            containers_steps_ui):
        """**Scenario:** Verify that public container url is available.

        **Steps:**

        #. Create public container using UI
        #. Create folder using UI
        #. Check folder is available by public url
        #. Delete folder

        **Teardown:**

        #. Delete container using UI
        """
        container_name = next(utils.generate_ids('container'))
        create_container_ui(container_name, public=True)

        with containers_steps_ui.get_container(container_name):
            container_info = containers_steps_ui.get_container_info(
                container_name)

            folder_name = next(utils.generate_ids('folder'))
            containers_steps_ui.create_folder(folder_name)

            containers_steps_ui.check_folder_avaiable_by_public_url(
                folder_name, container_info['public_url'])

            containers_steps_ui.delete_folder(folder_name)

    @pytest.mark.idempotent_id('27f9647e-a7be-454b-95c5-fe1aa84d665d',
                               any_one='admin')
    @pytest.mark.idempotent_id('8c627f7b-c2c9-4421-91e9-d90bc47346c3',
                               any_one='user')
    def test_upload_file_to_container(self, container, containers_steps_ui):
        """**Scenario:** Verify that one can upload file to container.

        **Setup:**

        #. Create container using UI

        **Steps:**

        #. Upload file to container
        #. Delete file from container

        **Teardown:**

        #. Delete container using UI
        """
        with containers_steps_ui.get_container(container.name):
            file_path = next(utils.generate_files())

            file_name = containers_steps_ui.upload_file(file_path)
            containers_steps_ui.delete_file(file_name)

    @pytest.mark.idempotent_id('762249c5-ae19-4480-9295-b51501c0c817',
                               any_one='admin')
    @pytest.mark.idempotent_id('6031f347-8a36-4939-b2b8-f01957511d3c',
                               any_one='user')
    def test_upload_file_to_folder(self, container, containers_steps_ui):
        """**Scenario:** Verify that one can upload file to folder.

        **Setup:**

        #. Create container using UI

        **Steps:**

        #. Create folder using UI
        #. Upload file to folder
        #. Delete file from folder
        #. Delete folder

        **Teardown:**

        #. Delete container using UI
        """
        with containers_steps_ui.get_container(container.name):
            folder_name = next(utils.generate_ids('folder'))
            containers_steps_ui.create_folder(folder_name)

            with containers_steps_ui.get_folder(folder_name):
                file_path = next(utils.generate_files())
                file_name = containers_steps_ui.upload_file(file_path)
                containers_steps_ui.delete_file(file_name)

            containers_steps_ui.delete_folder(folder_name)
