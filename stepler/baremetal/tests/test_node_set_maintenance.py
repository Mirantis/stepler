"""
---------------
Baremetal tests
---------------
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


@pytest.mark.idempotent_id('d459088e-fa91-4150-9753-2ec3b90850ed')
def test_set_node_maintenance(ironic_node_steps):
    """**Scenario:** Verify that ironic node maintenance can be changed.

    **Steps:**
    #. Create ironic node
    #. Change ironic node maintenance

    **Teardown:**

    #. Delete ironic node
    """
    node = ironic_node_steps.create_ironic_nodes()
    ironic_node_steps.set_ironic_nodes_maintenance(nodes=node, state=True)
