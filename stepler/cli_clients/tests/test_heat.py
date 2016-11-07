"""
--------------
Heat CLI tests
--------------
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

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('1fb54c78-20f5-459b-9515-3d7caf73ed64')
@pytest.mark.usefixtures('stacks_cleanup')
def test_stack_create_from_file(empty_heat_template_path, cli_heat_steps,
                                stack_steps):
    """**Scenario:** Create stack from template file with CLI.

    **Setup:**

    #. Upload template to node

    **Steps:**

    #. Create stack with template from file
    #. Check that stack is exists

    **Teardown:**

    #. Delete stack
    """
    parameters = {'param': 'string'}
    stack_name = next(utils.generate_ids('stack'))
    stack = cli_heat_steps.create_stack(
        name=stack_name,
        template_file=empty_heat_template_path,
        parameters=parameters)
    stack_steps.check_presence(
        stack['id'], timeout=config.STACK_CREATION_TIMEOUT)


@pytest.mark.idempotent_id('60d6d01b-5e52-42c5-951d-ff487ba14cd4')
@pytest.mark.usefixtures('stacks_cleanup')
def test_stack_create_from_url(cli_heat_steps, stack_steps):
    """**Scenario:** Create stack from template url with CLI.

    **Steps:**

    #. Create stack from URL
    #. Check that stack exists

    **Teardown:**

    #. Delete stack
    """
    stack_name = next(utils.generate_ids('stack'))
    stack = cli_heat_steps.create_stack(
        name=stack_name,
        template_url=config.HEAT_SIMPLE_TEMPLATE_URL)
    stack_steps.check_presence(
        stack['id'], timeout=config.STACK_CREATION_TIMEOUT)


@pytest.mark.idempotent_id('6108fc79-7173-4e4a-a061-97acb8432717')
@pytest.mark.usefixtures('stacks_cleanup')
def test_stack_delete(empty_stack, cli_heat_steps, stack_steps):
    """**Scenario:** Delete stack with heat CLI.

    **Setup:**

    #. Create stack

    **Steps:**

    #. Delete stack
    #. Check that stack is not exist
    """
    cli_heat_steps.delete_stack({'id': empty_stack.id})
    stack_steps.check_presence(
        empty_stack, present=False, timeout=config.STACK_DELETING_TIMEOUT)


@pytest.mark.idempotent_id('bf105cea-1ada-47b5-aae1-7a59cfa4617e')
def test_stack_preview(empty_heat_template_path, cli_heat_steps):
    """**Scenario:** Preview stack with heat CLI.

    **Setup:**

    #. Upload template to node

    **Steps:**

    #. Preview stack
    """
    parameters = {'param': 'string'}
    stack_name = next(utils.generate_ids('stack'))
    cli_heat_steps.preview_stack(
        name=stack_name,
        template_file=empty_heat_template_path,
        parameters=parameters)


@pytest.mark.idempotent_id('f115c4f1-5293-46bc-9b3f-736a2a19d5ab')
@pytest.mark.usefixtures('stacks_cleanup')
def test_stack_show(empty_stack, cli_heat_steps, stack_steps):
    """**Scenario:** Show stack with heat CLI.

    **Setup:**

    #. Create stack

    **Steps:**

    #. Call ``heat stack-show``
    #. Check that result has correct stack_name and id
    """
    cli_heat_steps.show_stack(empty_stack.to_dict())
