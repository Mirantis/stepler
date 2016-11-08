"""
--------------
Heat CLI steps
--------------
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

from hamcrest import assert_that, is_, is_not, empty, has_entries  # noqa H301

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker

__all__ = ['CliHeatSteps']


class CliHeatSteps(base.BaseCliSteps):
    """Heat CLI steps."""

    @steps_checker.step
    def create_stack(self,
                     name,
                     template_file=None,
                     template_url=None,
                     parameters=None,
                     check=True):
        """Step to create stack.

        Args:
            name (str): name of stack
            template_file (str, optional): path to yaml template
            template_url (str, optional): template url
            parameters (dict|None): parameters for template
            check (bool): flag whether check step or not

        Returns:
            dict: heat stack
        """
        parameters = parameters or {}

        err_msg = 'One of `template_file` or `template_url` should be passed.'
        assert_that(any([template_file, template_url]), is_(True), err_msg)

        cmd = 'heat stack-create ' + name
        if template_file:
            cmd += ' -f ' + template_file
        elif template_url:
            cmd += ' -u ' + template_url
        for key, value in parameters.items():
            cmd += ' --parameters {}={}'.format(key, value)
        cmd += ' --poll'

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_CREATION_TIMEOUT, check=check)
        stack_table = output_parser.tables(stdout)[-1]
        stack = {key: value for key, value in stack_table['values']}

        return stack

    @steps_checker.step
    def delete_stack(self, stack, check=True):
        """Step to delete stack.

        Args:
            stack (dict): stack to delete
            check (bool): flag whether to check step or not
        """
        cmd = 'heat stack-delete {}'.format(stack['id'])
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_DELETING_TIMEOUT, check=check)

        if check:
            assert_that(stderr, is_(empty()))

    @steps_checker.step
    def preview_stack(self, name, template_file, parameters=None, check=True):
        """Step to preview stack.

        Args:
            name (str): name of stack preview
            template_file (str): path to stack template file
            parameters (dict, optional): additional parameters to template
            check (bool): flag whether to check step or not

        Returns:
            dict: stack preview result

        Raises:
            AssertionError: if stack preview returns not 'None' stack's id
        """
        parameters = parameters or {}
        cmd = 'heat stack-preview {name} -f {file}'.format(name=name,
                                                           file=template_file)
        for key, value in parameters.items():
            cmd += ' --parameters {}={}'.format(key, value)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_PREVIEW_TIMEOUT, check=check)

        stack_table = output_parser.table(stdout)
        stack = {key: value for key, value in stack_table['values']}
        if check:
            assert_that(stack['id'], is_('None'))
        return stack

    @steps_checker.step
    def show_stack(self, stack, check=True):
        """Step to show stack.

        Args:
            stack (dict): heat stack to show
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if output contains wrong stack's name or id
        """
        cmd = 'heat stack-show {}'.format(stack['id'])
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_SHOW_TIMEOUT, check=check)

        stack_table = output_parser.table(stdout)
        show_result = {key: value for key, value in stack_table['values']}
        if check:
            assert_that(
                show_result,
                has_entries(
                    stack_name=stack['stack_name'], id=stack['id']))

    @steps_checker.step
    def update_stack(self, stack, template_file, parameters=None, check=True):
        """Step to update stack.

        Args:
            stack (dict): heat stack to update
            template_file (str): path to stack template file
            parameters (list, optional): additional parameters to template
            check (bool): flag whether to check step or not
        """
        parameters = parameters or {}
        cmd = 'heat stack-update {id} -f {file}'.format(id=stack['id'],
                                                        file=template_file)
        for key, value in parameters.items():
            cmd += ' --parameters {}={}'.format(key, value)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_UPDATING_TIMEOUT, check=check)

    @steps_checker.step
    def cancel_stack_update(self, stack, check=True):
        """Step to cancel stack update.

        Args:
            stack (dict): heat stack to cancel update
            check (bool): flag whether to check step or not
        """
        cmd = 'heat stack-cancel-update {}'.format(stack['id'])
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_UPDATING_TIMEOUT, check=check)

    @steps_checker.step
    def get_stack_events_list(self, stack, check=True):
        """Step to show stack's events list.

        Args:
            stack (dict): heat stack to show events list
            check (bool): flag whether to check step or not

        Returns:
            list: list of stack events
        """
        cmd = 'heat event-list {}'.format(stack['id'])
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_UPDATING_TIMEOUT, check=check)

        events = output_parser.listing(stdout)
        if check:
            assert_that(events, is_not(empty()))
        return events

    @steps_checker.step
    def suspend_stack(self, stack, check=True):
        """Step to suspend stack.

        Args:
            stack (dict): heat stack to suspend
            check (bool): flag whether to check step or not
        """
        cmd = 'heat action-suspend {}'.format(stack['id'])
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_SUSPEND_TIMEOUT, check=check)

    @steps_checker.step
    def resume_stack(self, stack, check=True):
        """Step to resume stack.

        Args:
            stack (dict): heat stack to resume
            check (bool): flag whether to check step or not
        """
        cmd = 'heat action-resume {}'.format(stack['id'])
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_RESUME_TIMEOUT, check=check)
