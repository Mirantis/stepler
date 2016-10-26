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

from hamcrest import assert_that, is_, empty  # noqa H301

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
        cmd = 'heat stack-delete {0[id]}'.format(stack)
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_DELETING_TIMEOUT, check=check)

        if check:
            assert_that(stderr, is_(empty()))
