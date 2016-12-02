"""
-----------------
Ironic node tests
-----------------
"""

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pytest


@pytest.mark.idempotent_id('340cec4f-179e-4ebd-843a-67977d666a67')
def test_node_create(ironic_node):
    """**Scenario:** Verify that ironic node can be created and deleted.

    **Setup:**

    #. Create ironic node

    **Teardown:**

    #. Delete ironic node
    """


@pytest.mark.idempotent_id('b08d3461-fe78-479d-8acc-00267ca79b5f')
def test_ironic_node_name(ironic_node_steps):
    """**Scenario:** Verify that ironic node can be created with name
    which has dot.

    **Steps:**

    #. Create ironic node with name 'stepler.test'

    **Teardown:**

    #. Delete ironic node
    """
    ironic_node_steps.create_ironic_nodes(nodes_names=["stepler.test"])
