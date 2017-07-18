"""
----------
Auth tests
----------
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


@pytest.mark.idempotent_id('7f35902f-81ca-4a69-a7dc-5b538195c14c',
                           any_one='admin')
@pytest.mark.idempotent_id('ca21eba8-932d-4a8b-b691-fbdc54448c8d',
                           any_one='user')
@pytest.mark.usefixtures('any_one')
def test_login(credentials, auth_steps):
    """**Scenario:** Verify that one can login and logout.

    **Steps:**

    #. Login to horizon
    #. Switch to user project
    #. Logout
    """
    auth_steps.login(credentials.username, credentials.password)
    auth_steps.switch_project(credentials.project_name)
    auth_steps.logout()


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):

    @pytest.mark.idempotent_id('d86ee186-66d8-11e7-8094-5404a69126b9')
    def test_check_time_opening_pages(self, networks_steps_ui, auth_steps,
                                      keypairs_steps_ui, routers_steps_ui):
        """**Scenario:** Verify that time opening pages less 1 sec.

        # Test for covering bug https://bugs.launchpad.net/mos/+bug/1593456

        **Steps:**

        #. Check time authorization into Horizon
        #. Check time opening of Keypairs tab
        #. Check time opening of Networks tab
        #. Check time opening of Routers tab
        """
        auth_steps.check_login_time()
        keypairs_steps_ui.check_keypairs_time()
        networks_steps_ui.check_networks_time()
        routers_steps_ui.check_routers_time()
