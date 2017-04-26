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
        """**Scenario:** Verify that one can download RCv2.

        **Steps:**

        #. Download rc v2 file using UI
        """
        api_access_steps_ui.download_rc_v2()

    @pytest.mark.idempotent_id('3d850ba2-a4c7-4b20-b1dc-5b2b00dc7017',
                               any_one='admin')
    @pytest.mark.idempotent_id('8bd7424a-db01-4978-b933-380afa68f78d',
                               any_one='user')
    def test_download_rc_v3(self, api_access_steps_ui):
        """**Scenario:** Verify that one can download RCv3.

        **Steps:**

        #. Download rc v3 file using UI
        """
        api_access_steps_ui.download_rc_v3()

    @pytest.mark.idempotent_id('c414f5b0-c098-48ea-b99b-6e37597bcd7a',
                               any_one='admin')
    @pytest.mark.idempotent_id('5bf8ab88-2839-42af-afa0-c2cc5211f774',
                               any_one='user')
    def test_view_credentials(self, api_access_steps_ui):
        """**Scenario:** Verify that one can view credentials.

        **Steps:**

        #. View credentials using UI
        """
        api_access_steps_ui.view_credentials()
