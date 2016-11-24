"""
---------------------
Ironic API node tests
---------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest


@pytest.mark.idempotent_id('42f8d374-fe5b-4efb-ae09-9aef72a93010')
def test_nodes_get(api_ironic_steps_v1):
    """**Scenario:** Verify that ironic nodes can be taken via API.

    **Steps:**

    #. Get ironic nodes
    """
    api_ironic_steps_v1.get_ironic_nodes()


@pytest.mark.idempotent_id('21d65216-78b1-4206-bd8b-faad76c079dc')
def test_node_create(api_ironic_steps_v1, ironic_node_steps):
    """**Scenario:** Verify that ironic node can be created via API.

    **Steps:**

    #. Create ironic node
    """
    api_ironic_steps_v1.create_ironic_nodes()
