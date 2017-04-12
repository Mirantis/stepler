"""
------------
Router tests
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


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any user."""

    @pytest.mark.idempotent_id('baa62875-afbe-46bc-9063-9d62f37f9e49',
                               any_one='admin')
    @pytest.mark.idempotent_id('64927ee0-25a4-4b43-8bfe-097ae7d4a3b6',
                               any_one='user')
    def test_create_delete_router(self, routers_steps_ui):
        """**Scenario:** Verify that user can create and delete router.

        **Steps:**

        #. Create router using UI
        #. Delete router using UI
        """
        router_name = routers_steps_ui.create_router()
        routers_steps_ui.delete_router(router_name)
