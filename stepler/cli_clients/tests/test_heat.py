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
def test_stack_show(empty_stack, cli_heat_steps):
    """**Scenario:** Show stack with heat CLI.

    **Setup:**

    #. Create stack

    **Steps:**

    #. Call ``heat stack-show``
    #. Check that result has correct stack_name and id

    **Teardown:**

    #. Delete stack
    """
    cli_heat_steps.show_stack(empty_stack.to_dict())


@pytest.mark.idempotent_id('9db8f266-106d-436f-ac8b-05ee58fab674')
def test_stack_update(empty_heat_template_path,
                      empty_stack,
                      cli_heat_steps,
                      stack_steps):
    """**Scenario:** Update stack with heat CLI.

    **Setup:**

    #. Create stack

    **Steps:**

    #. Update stack with CLI
    #. Check that stack status is ``update_complete``

    **Teardown:**

    #. Delete stack
    """
    parameters = {'param': 'string2'}
    cli_heat_steps.update_stack(
        empty_stack.to_dict(),
        template_file=empty_heat_template_path,
        parameters=parameters)
    stack_steps.check_status(
        empty_stack,
        config.HEAT_COMPLETE_STATUS,
        transit_statuses=[config.HEAT_IN_PROGRESS_STATUS],
        timeout=config.STACK_UPDATING_TIMEOUT)


@pytest.mark.idempotent_id('809fdf33-e528-40dd-9042-e619072e1ab4')
def test_cancel_stack_update(cirros_image,
                             flavor,
                             public_network,
                             network,
                             subnet,
                             router,
                             add_router_interfaces,
                             create_flavor,
                             read_heat_template,
                             create_stack,
                             cli_heat_steps,
                             stack_steps):
    """**Scenario:** Cancel stack updating with heat CLI.

    Note:
        This test verifies bug #1570825

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create network
    #. Create subnet
    #. Create router
    #. Set router default gateway to public network

    **Steps:**

    #. Create 2'nd flavor
    #. Add router interface to created network
    #. Read Heat resources template from file
    #. Create stack with template with parameters
    #. Start stack updating with 2'nd flavor
    #. Cancel stack updating with CLI
    #. Check stack status

    **Teardown:**

    #. Delete stack
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete flavors
    #. Delete cirros image
    """
    flavor2_name = next(utils.generate_ids('flavor'))
    flavor2 = create_flavor(flavor2_name, ram=2048, vcpus=1, disk=5)

    add_router_interfaces(router, [subnet])

    template = read_heat_template('nova_server')
    stack_name = next(utils.generate_ids('stack'))
    parameters = {
        'image': cirros_image.id,
        'flavor': flavor.id,
        'network': network['id'],
    }
    stack = create_stack(stack_name, template=template, parameters=parameters)

    parameters['flavor'] = flavor2.id
    stack_steps.update_stack(stack, template=template, parameters=parameters,
                             check=False
                             )

    cli_heat_steps.cancel_stack_update(stack.to_dict())
    stack_steps.check_status(
        stack,
        config.HEAT_COMPLETE_STATUS,
        transit_statuses=[config.HEAT_IN_PROGRESS_STATUS],
        timeout=config.STACK_UPDATING_TIMEOUT)


@pytest.mark.idempotent_id('37599b0d-0c2f-483e-98b9-4e6756476c51')
def test_stack_show_events_list(empty_stack, cli_heat_steps):
    """**Scenario:** Show stack events_list with heat CLI.

    **Setup:**

    #. Create stack

    **Steps:**

    #. Call ``heat event-list``
    #. Check that result table is not empty

    **Teardown:**

    #. Delete stack
    """
    cli_heat_steps.get_stack_events_list(empty_stack.to_dict())


@pytest.mark.idempotent_id('050e4422-5aa4-44da-b5f4-b69bde929037')
def test_stack_suspend(empty_stack, cli_heat_steps, stack_steps):
    """**Scenario:** Suspend stack with heat CLI.

    **Setup:**

    #. Create stack

    **Steps:**

    #. Call ``heat action-suspend``
    #. Check that stack's `stack_status` is SUSPEND_COMPLETE

    **Teardown:**

    #. Delete stack
    """
    cli_heat_steps.suspend_stack(empty_stack.to_dict())
    stack_steps.check_stack_status(
        empty_stack,
        config.STACK_STATUS_SUSPEND_COMPLETE,
        timeout=config.STACK_SUSPEND_TIMEOUT)


@pytest.mark.idempotent_id('8c897eeb-0916-4390-b2f5-a61551c35852')
def test_stack_resume(empty_stack,
                      cli_heat_steps,
                      stack_steps):
    """**Scenario:** Resume stack with heat CLI.

    **Setup:**

    #. Create stack

    **Steps:**

    #. Suspend stack
    #. Call ``heat action-resume``
    #. Check that stack's `stack_status` is RESUME_COMPLETE

    **Teardown:**

    #. Delete stack
    """
    stack_steps.suspend(empty_stack)
    cli_heat_steps.resume_stack(empty_stack.to_dict())
    stack_steps.check_stack_status(
        empty_stack,
        config.STACK_STATUS_RESUME_COMPLETE,
        timeout=config.STACK_RESUME_TIMEOUT)


@pytest.mark.idempotent_id('13031bc9-19e5-4ab9-8478-968f8fc925f2')
def test_stack_check_resources(empty_stack, cli_heat_steps, stack_steps):
    """**Scenario:** Check stack resources with heat CLI.

    **Setup:**

    #. Create stack

    **Steps:**

    #. Call ``heat action-check``
    #. Check that stack's `stack_status` is CHECK_COMPLETE

    **Teardown:**

    #. Delete stack
    """
    cli_heat_steps.stack_resources_check(empty_stack.to_dict())
    stack_steps.check_stack_status(
        empty_stack,
        config.STACK_STATUS_CHECK_COMPLETE,
        timeout=config.STACK_CHECK_TIMEOUT)
