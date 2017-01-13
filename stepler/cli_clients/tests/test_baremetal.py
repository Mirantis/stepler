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

pytestmark = [pytest.mark.requires("ironic_nodes_count >= 1")]


@pytest.mark.idempotent_id('4bd3e2ac-be73-423e-8026-39a151592076')
def test_ironic_node_list(cli_ironic_steps):
    """**Scenario:** Ironic node-list works via shell.

    **Steps:**

    #. Execute in shell ``ironic node-list``
    """
    cli_ironic_steps.ironic_node_list()


@pytest.mark.idempotent_id('efdc39ca-27c3-49c1-9f76-1196d02bd3fe')
def test_ironic_port_list(cli_ironic_steps):
    """**Scenario:** Ironic port-list works via shell.

    **Steps:**

    #. Execute in shell ``ironic port-list``
    """
    cli_ironic_steps.ironic_port_list()


@pytest.mark.idempotent_id('dbec9c3f-fa7d-4823-8b6f-b3f54f1235ad')
def test_ironic_chassis_list(cli_ironic_steps):
    """**Scenario:** Ironic chassis-list works via shell.

    **Steps:**

    #. Execute in shell ``ironic chassis-list``
    """
    cli_ironic_steps.ironic_chassis_list()


@pytest.mark.idempotent_id('2d93c9c6-7f23-485d-a36b-41924ae0e393')
def test_ironic_driver_list(cli_ironic_steps):
    """**Scenario:** Ironic driver-list works via shell.

    **Steps:**

    #. Execute in shell ``ironic driver-list``
    """
    cli_ironic_steps.ironic_driver_list()
