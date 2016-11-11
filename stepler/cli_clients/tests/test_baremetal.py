"""
---------------------------
Tests for Ironic CLI client
---------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest


@pytest.mark.idempotent_id('4bd3e2ac-be73-423e-8026-39a151592076')
def test_ironic_list(cli_ironic_steps):
    """**Scenario:** Ironic node-list works via shell.

    **Setup:**

    #. Create Ironic node

    **Steps:**

    #. Execute in shell ``ironic node-list``

    **Teardown:**

    #. Remove Ironic node
    """
    cli_ironic_steps.ironic_node_list()
