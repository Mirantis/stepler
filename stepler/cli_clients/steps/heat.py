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

import re

from hamcrest import assert_that, equal_to, is_not, empty  # noqa
import six
from tempest.lib.cli import output_parser

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import steps_checker

__all__ = ['CliHeatSteps']


class CliHeatSteps(base.BaseCliSteps):
    """Heat CLI steps."""

    def _get_last_table(self, output):
        row_delimiters = list(re.finditer(r'^\+[+-]+\+$', output, re.M))
        start = row_delimiters[-3].start()
        end = row_delimiters[-1].end()
        return output[start:end + 1]

    def _show_to_dict(self, output):
        obj = {}
        items = output_parser.listing(output)
        for item in items:
            obj[item['Property']] = six.text_type(item['Value'])
        return obj

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
        """
        cmd = 'heat stack-create {} -f {}'.format(name, template_file)
        parameters = parameters or {}
        for key, value in parameters.items():
            cmd += ' --parameters {}={}'.format(key, value)
        cmd += ' --poll'
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.STACK_CREATION_TIMEOUT, check=check)
        stack_table = self._get_last_table(stdout)
        stack = self._show_to_dict(stack_table)

        return stack
