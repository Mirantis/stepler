"""
---------------------------
Nova Rebuild Negative tests
---------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest


@pytest.mark.idempotent_id('280559ac-d000-4132-ab7e-6b75b1dfb1fd')
def test_rebuild_in_paused_state(cirros_image, server, server_steps):
    """**Scenario:** Try to rebuild an instance in Paused state.

    **Setup:**

    #. Create server

    **Steps:**

    #. Pause server
    #. Try to rebuild server
    #. Check that rebuild fails and exception is called

    **Teardown:**

    #. Delete server
    """
    server_steps.pause_server(server)
    server_steps.check_server_not_rebuilt_in_paused_state(
        server, cirros_image)


@pytest.mark.idempotent_id('f289dfcd-b63a-473d-90fb-1e099fe51c4b')
def test_rebuild_in_rescue_state(cirros_image, server, server_steps):
    """**Scenario:** Try to rebuild an instance in Rescued state.

    **Setup:**

    #. Create server

    **Steps:**

    #. Rescue server
    #. Try to rebuild server
    #. Check that rebuild fails and exception is called

    **Teardown:**

    #. Delete server
    """
    server_steps.rescue_server(server)
    server_steps.check_server_not_rebuilt_in_rescue_state(
        server, cirros_image)
