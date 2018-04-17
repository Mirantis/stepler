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

    @pytest.mark.idempotent_id('f624afef-8cdd-4aea-bdc3-066234212f00',
                               any_one='admin')
    @pytest.mark.idempotent_id('9f0a660e-2ed7-4b4b-8f72-7ea7733c22c5',
                               any_one='user')
    def test_stack_delete(self, empty_stack, stacks_steps_ui):
        """**Scenario:** Verify that anyone can delete stack.

        **Setup:**

        #. Create empty stack with API

        **Steps:**

        #. Delete stack with UI
        """
        stacks_steps_ui.delete_stack(empty_stack)

    @pytest.mark.idempotent_id('3a24328e-bd82-4d3b-8cab-9fbbb221d408',
                               any_one='admin')
    @pytest.mark.idempotent_id('76fa1807-ab4e-4d48-83e8-de4a478419f3',
                               any_one='user')
    def test_stacks_delete(self, create_stack, read_heat_template,
                           empty_stack, stacks_steps_ui):
        """**Scenario:** Verify that anyone can delete stacks.

        **Setup:**

        #. Create 2 stacks with API

        **Steps:**

        #. Delete stacks as bunch using UI
        """
        template = read_heat_template('random_str')
        stack = create_stack(next(utils.generate_ids()), template)
        stacks_steps_ui.delete_stacks([stack, empty_stack])

    @pytest.mark.idempotent_id('f5a802b9-45b9-49a9-a41b-f3d9ad363806',
                               any_one='admin')
    @pytest.mark.idempotent_id('3c7237f5-faf9-423e-b90e-3fa39e94b8e5',
                               any_one='user')
    def test_view_stack(self, empty_stack, stacks_steps_ui):
        """**Scenario:** Verify that anyone can view stack info.

        **Setup:**

        #. Create empty stack with API

        **Steps:**

        #. View stack

        **Teardown:**

        #. Delete created stack
        """
        stacks_steps_ui.view_stack(empty_stack)

    @pytest.mark.idempotent_id('ae5854be-2d88-4130-98d3-55004a4703ef',
                               any_one='admin')
    @pytest.mark.idempotent_id('e11972fe-00be-4d3d-b987-f92504073a5c',
                               any_one='user')
    def test_preview_stack(self, stacks_steps_ui):
        """**Scenario:** Verify that anyone can preview stack.

        **Steps:**

        #. Preview stack using UI
        """
        stacks_steps_ui.preview_stack(next(utils.generate_ids()))

    @pytest.mark.smoke
    @pytest.mark.idempotent_id('35ad523c-995f-478d-bbeb-9cdfba9a5590',
                               any_one='admin')
    @pytest.mark.idempotent_id('8779b583-d089-41b7-a2d2-f5d40816c52a',
                               any_one='user')
    def test_check_stack(self, empty_stack, stacks_steps_ui):
        """**Scenario:** Verify that anyone can check stack status.

        **Setup:**

        #. Create empty stack with API

        **Steps:**

        #. Check stack status

        **Teardown:**

        #. Delete stack with API
        """
        stacks_steps_ui.check_stack(empty_stack)

    @pytest.mark.idempotent_id('2aee4f6a-e15e-435d-9e5f-d430152ad1d2',
                               any_one='admin')
    @pytest.mark.idempotent_id('4f1fb5cc-eca7-4751-b523-32cad3e5ce3f',
                               any_one='user')
    def test_suspend_and_resume_stack(self, empty_stack, stacks_steps_ui):
        """**Scenario:** Verify that anyone can suspend and resume stack.

        **Setup:**

        #. Create empty stack with API

        **Steps:**

        #. Suspend stack
        #. Resume stack

        **Teardown:**

        #. Delete stack with API
        """
        stacks_steps_ui.suspend_stack(empty_stack)
        stacks_steps_ui.resume_stack(empty_stack)


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Tests for admin only."""

    @pytest.mark.idempotent_id('8381d3ff-9f94-465f-a127-c84d328e14a4')
    def test_create_stack(self, credentials, keypair, stacks_cleanup,
                          stacks_steps_ui):
        """**Scenario:** Verify that admin can create and delete stack.

        **Steps:**

        #. Create stack using UI
        """
        stack_name = next(utils.generate_ids())
        stacks_steps_ui.create_stack(stack_name=stack_name,
                                     admin_password=credentials.password,
                                     keypair=keypair)

    @pytest.mark.idempotent_id('570365c4-f4ab-48f3-8968-18fa64f93ae4')
    def test_change_stack_template(self, credentials, empty_stack,
                                   stacks_steps_ui):
        """**Scenario:** Verify that admin can change template of stack.

        **Setup:**

        #. Create empty stack with API

        **Steps:**

        #. Change stack template

        **Teardown:**

        #. Delete stack with API
        """
        stacks_steps_ui.change_stack_template(
            empty_stack, admin_password=credentials.password)
