"""
-----------------
Floating IP tests
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


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('95546c8c-775a-4527-b92b-83cf56db999d')
    def test_floating_ip_associate(self, horizon_server, floating_ip,
                                   floating_ips_steps_ui):
        """**Scenario:** Verify that admin can associate floating IP.

        **Setup:**

        #. Create floating IP using API
        #. Create server using API

        **Steps:**

        #. Associate floating IP to server using UI

        **Teardown:**

        #. Delete floating IP using API
        #. Delete server using API
        """
        floating_ips_steps_ui.associate_floating_ip(floating_ip.ip,
                                                    horizon_server.name)


@pytest.mark.usefixtures('user_only')
class TestUserOnly(object):
    """Tests for user only."""

    @pytest.mark.idempotent_id('57d7c23a-463e-49b7-843f-09ded9686fb9')
    def test_floating_ip_associate(self, horizon_server_with_private_image,
                                   floating_ip,floating_ips_steps_ui):

        """**Scenario:** Verify that user can associate floating IP.

        **Setup:**

        #. Create floating IP using API
        #. Create server using API

        **Steps:**

        #. Associate floating IP to server using UI

        **Teardown:**

        #. Delete floating IP using API
        #. Delete server using API
        """
        floating_ips_steps_ui.associate_floating_ip(floating_ip.ip,
                                                    horizon_server_with_private_image.name)

