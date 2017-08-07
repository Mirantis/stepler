"""
-----------------
Credentials tests
-----------------
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


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any one."""

    @pytest.mark.idempotent_id('b18a6dbe-f98c-41fa-ace7-dede0df0c8ef',
                               any_one='admin')
    @pytest.mark.idempotent_id('3b793f66-6e89-4ac7-b359-ad8c9787593f',
                               any_one='user')
    def test_download_rc_v2(self, api_access_steps_ui):
        """**Scenario:** Verify that user can download RCv2.

        **Steps:**

        #. Download rc v2 file using UI
        """
        api_access_steps_ui.download_rc_v2()

    @pytest.mark.idempotent_id('3d850ba2-a4c7-4b20-b1dc-5b2b00dc7017',
                               any_one='admin')
    @pytest.mark.idempotent_id('8bd7424a-db01-4978-b933-380afa68f78d',
                               any_one='user')
    def test_download_rc_v3(self, api_access_steps_ui):
        """**Scenario:** Verify that user can download RCv3.

        **Steps:**

        #. Download rc v3 file using UI
        """
        api_access_steps_ui.download_rc_v3()

    @pytest.mark.idempotent_id('a38d81c2-7b67-11e7-838c-1b220e28c682',
                               any_one='admin')
    @pytest.mark.idempotent_id('a4909b40-7b67-11e7-804d-abae3a40e158',
                               any_one='user')
    def test_download_rc_v3_via_menu(self, api_access_steps_ui):
        """**Scenario:** Verify that user can download RCv3 via menu.

        **Steps:**

        #. Download rc v3 file via menu using UI
        """
        api_access_steps_ui.download_rc_v3_via_menu()

    @pytest.mark.idempotent_id('a6ed9d2a-ae40-45ca-92c9-0034cbb425b1',
                               any_one='admin')
    @pytest.mark.idempotent_id('596710b9-1f77-4db9-9a77-f5733a5708ff',
                               any_one='user')
    def test_download_ec2(self, api_access_steps_ui):
        """**Scenario:** Verify that user can download EC2 credentials.

        **Steps:**

        #. Download ec2 file using UI
        """
        api_access_steps_ui.download_ec2()

    @pytest.mark.idempotent_id('c414f5b0-c098-48ea-b99b-6e37597bcd7a',
                               any_one='admin')
    @pytest.mark.idempotent_id('5bf8ab88-2839-42af-afa0-c2cc5211f774',
                               any_one='user')
    def test_view_credentials(self, api_access_steps_ui):
        """**Scenario:** Verify that user can view credentials.

        **Steps:**

        #. View credentials using UI
        """
        api_access_steps_ui.view_credentials()


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('5d3a55ec-5100-11e7-83e0-b33e26fe0aed')
    def test_download_rc_v2_non_ascii_project_name(self,
                                                   project_name_non_ascii,
                                                   api_access_steps_ui):
        """**Scenario:** Verify that RCv2 is correct with non-ASCII project name.

        **Setup:**

        #. Create project with non-ASCII name
        #. Switch to project with non-ASCII name

        **Steps:**

        #. Download RCv2 file using UI

        **Teardown:**

        #. Delete project with non-ASCII name
        """

        api_access_steps_ui.download_rc_v2()
