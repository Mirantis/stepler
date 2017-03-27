"""
--------------------------
Openstack CLI client steps
--------------------------
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

import json

from hamcrest import (assert_that, empty, has_entries, is_not,
                      equal_to)  # noqa: H301
import yaml

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import steps_checker


class CliOpenstackSteps(base.BaseCliSteps):
    """CLI openstack client steps."""

    @steps_checker.step
    def server_list(self, check=True):
        """Step to get server list.

        Args:
            check (bool): flag whether to check result or not

        Returns:
            str: result of command shell execution

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        cmd = 'openstack server list'
        result = self.execute_command(
            cmd, timeout=config.SERVER_LIST_TIMEOUT, check=check)
        return result

    @steps_checker.step
    def baremetal_node_list(self, check=True):
        """Step to get baremetal node list.

        Args:
            check (bool): flag whether to check result or not

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        cmd = 'openstack baremetal list'
        self.execute_command(cmd,
                             timeout=config.SERVER_LIST_TIMEOUT,
                             check=check)

    @steps_checker.step
    def create_stack(self, name, template_file, parameters=None, check=True):
        """Step to create stack.

        Args:
            name (str): name of stack
            template_file (str): path to yaml template
            parameters (dict|None): parameters for template
            check (bool): flag whether check step or not

        Returns:
            dict: heat stack

        Raises:
            AssertionError: if command exit_code is not 0
        """
        parameters = parameters or {}

        cmd = ('openstack stack create -f json --wait '
               '-t {template} {name}').format(
                   template=template_file, name=name)
        for key, value in parameters.items():
            cmd += ' --parameter {}={}'.format(key, value)

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_CREATION_TIMEOUT, check=check)
        stack_data = '{' + stdout.split('{\n', 1)[-1]

        return json.loads(stack_data)

    @steps_checker.step
    def delete_stack(self, stack, check=True):
        """Step to delete stack.

        Args:
            stack (obj): stack to delete
            check (bool): flag whether to check step or not
        """
        cmd = 'openstack stack delete --yes --wait {}'.format(stack.id)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_DELETING_TIMEOUT, check=check)
        if check:
            assert_that(stderr, empty())

    @steps_checker.step
    def show_stack(self, stack, check=True):
        """Step to show stack.

        Args:
            stack (obj): heat stack to show
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if output contains wrong stack's name or id
        """
        cmd = 'openstack stack show -f json {}'.format(stack.id)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_SHOW_TIMEOUT, check=check)

        show_result = json.loads(stdout)
        if check:
            assert_that(
                show_result,
                has_entries(
                    stack_name=stack.stack_name, id=stack.id))

    @steps_checker.step
    def update_stack(self, stack, template_file, parameters=None, check=True):
        """Step to update stack.

        Args:
            stack (obj): heat stack to update
            template_file (str): path to stack template file
            parameters (list, optional): additional parameters to template
            check (bool): flag whether to check step or not
        """
        parameters = parameters or {}
        cmd = ('openstack stack update --wait '
               '{id} -t {file}').format(
                   id=stack.id, file=template_file)
        for key, value in parameters.items():
            cmd += ' --parameter {}={}'.format(key, value)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_UPDATING_TIMEOUT, check=check)

    @steps_checker.step
    def cancel_stack_update(self, stack, check=True):
        """Step to cancel stack update.

        Args:
            stack (obj): heat stack to cancel update
            check (bool): flag whether to check step or not
        """
        cmd = 'openstack stack cancel --wait {}'.format(stack.id)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_UPDATING_TIMEOUT, check=check)

    @steps_checker.step
    def get_stack_events_list(self, stack, check=True):
        """Step to show stack's events list.

        Args:
            stack (obj): heat stack to show events list
            check (bool): flag whether to check step or not

        Returns:
            list: list of stack events

        Raises:
            AssertionError: if events list is empty
        """
        cmd = 'openstack stack event list -f json {}'.format(stack.id)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_UPDATING_TIMEOUT, check=check)

        events = json.loads(stdout)
        if check:
            assert_that(events, is_not(empty()))
        return events

    @steps_checker.step
    def get_stack_event(self, stack, resource, event, check=True):
        """Step to get stack's events list.

        Args:
            stack (obj): heat stack
            resource (str): name of the resource the event belongs to
            event (str): ID of event to display details for
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if stack event is empty

        Returns:
            dict: stack event
        """
        cmd = ('openstack stack event show -f json '
               '{stack} {resource} {event}').format(
                   stack=stack.id, resource=resource, event=event)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_UPDATING_TIMEOUT, check=check)

        event = json.loads(stdout)
        if check:
            assert_that(event, is_not(empty()))
        return event

    @steps_checker.step
    def suspend_stack(self, stack, check=True):
        """Step to suspend stack.

        Args:
            stack (obj): heat stack
            check (bool): flag whether to check step or not
        """
        cmd = 'openstack stack suspend --wait {}'.format(stack.id)
        self.execute_command(cmd, timeout=config.STACK_SUSPEND_TIMEOUT,
                             check=check)

    @steps_checker.step
    def resume_stack(self, stack, check=True):
        """Step to resume stack.

        Args:
            stack (obj): heat stack
            check (bool): flag whether to check step or not
        """
        cmd = 'openstack stack resume --wait {}'.format(stack.id)
        self.execute_command(cmd, timeout=config.STACK_RESUME_TIMEOUT,
                             check=check)

    @steps_checker.step
    def stack_resources_check(self, stack, check=True):
        """Step to check stack resources.

        Args:
            stack (obj): heat stack
            check (bool): flag whether to check step or not
        """
        cmd = 'openstack stack check {}'.format(stack.id)
        self.execute_command(cmd, timeout=config.STACK_CLI_TIMEOUT,
                             check=check)

    @steps_checker.step
    def get_resource_type_template(self, resource_type, check=True):
        """Step to check stack resources.

        Args:
            resource_type (obj): heat resource type
            check (bool): flag whether to check step or not

        Returns:
            dict: resource template
        """
        cmd = ('openstack orchestration resource type show '
               '--template-type hot {}').format(resource_type.resource_type)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_CLI_TIMEOUT, check=check)
        template = yaml.load(stdout)
        return template

    @steps_checker.step
    def show_stack_output(self, stack, output, output_result, check=True):
        """Step to show a specific stack output.

        Args:
            stack (obj): heat stack
            output (str): name of output to show
            output_result (str): expected output result
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if output contains unexpected result
        """
        cmd = 'openstack stack output show -f json {0} {1}'.format(stack.id,
                                                                   output)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_SHOW_TIMEOUT, check=check)
        result = json.loads(stdout)

        if check:
            assert_that(result['output_value'], equal_to(output_result))
