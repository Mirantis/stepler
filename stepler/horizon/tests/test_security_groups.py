"""
--------------------
Security group tests
--------------------
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

    @pytest.mark.idempotent_id('bd1840c3-ac0c-4a36-ac63-d0182edfb6ec',
                               any_one='admin')
    @pytest.mark.idempotent_id('e41796c3-0f14-467c-80b0-98012d13bc1c',
                               any_one='user')
    def test_create_delete_security_group(self, access_steps_ui):
        """**Scenario:** Verify that user can create and delete security group.

        **Steps:**

        #. Create security group using UI
        #. Delete security group using UI
        """
        group_name = access_steps_ui.create_security_group()
        access_steps_ui.delete_security_group(group_name)

    @pytest.mark.idempotent_id('e0a53c7a-bb3f-485c-b51e-153cf0b0033f',
                               any_one='admin')
    @pytest.mark.idempotent_id('108ae5e7-a61a-4fd7-a6fb-2109102fe899',
                               any_one='user')
    def test_add_delete_rule(self, access_steps_ui, security_group):
        """**Scenario:** Verify that user can manage rules for security group.

        **Setup:**

        #. Create security group using API

        **Steps:**

        #. Add rule using UI
        #. Delete rule using UI

        **Teardown:**

        #. Remove security group using API
        """
        port_number = access_steps_ui.add_group_rule(security_group.name)
        access_steps_ui.delete_group_rule(port_number)
