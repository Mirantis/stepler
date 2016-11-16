"""
------------------------------
Ironic baremetal chassis tests
------------------------------
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


@pytest.mark.idempotent_id('cde24671-65b2-46f5-b8e5-e3ff087e4da6')
def test_chassis_create(create_ironic_chassis):
    """**Scenario:** Verify that ironic chassis can be created and deleted.

    **Steps:**

    #. Create ironic chassis
    #. Delete ironic chassis
    """
