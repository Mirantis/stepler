"""
------------
Stacks tests
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

from stepler.third_party import utils


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any one."""

    @pytest.mark.idempotent_id('f5a802b9-45b9-49a9-a41b-f3d9ad363806',
                               any_one='admin')
    @pytest.mark.idempotent_id('3c7237f5-faf9-423e-b90e-3fa39e94b8e5',
                               any_one='user')
    def test_view_stack(self, create_stack, stacks_steps_ui, read_heat_template):
        """**Scenario:** Verify that anyone can view stack info.

        **Setup:**

        #. Create stack with API

        **Steps:**

        #. View stack

        **Teardown:**

        #. Delete created stack
        """
        template = read_heat_template('random_str')
        stack = create_stack(next(utils.generate_ids()), template)
        stacks_steps_ui.view_stack(stack)

    @pytest.mark.smoke
    @pytest.mark.idempotent_id('35ad523c-995f-478d-bbeb-9cdfba9a5590',
                               any_one='admin')
    @pytest.mark.idempotent_id('8779b583-d089-41b7-a2d2-f5d40816c52a',
                               any_one='user')
    def test_check_stack(self, create_stack, stacks_steps_ui, read_heat_template):
        """**Scenario:** Verify that anyone can check stack status.

        **Setup:**

        #. Create stack with API

        **Steps:**

        #. Check stack status

        **Teardown:**

        #. Delete stack with API
        """
        template = read_heat_template('random_str')
        stack = create_stack(next(utils.generate_ids()), template)
        stacks_steps_ui.check_stack(stack)
