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

from hamcrest import assert_that, is_, is_not, empty, equal_to  # noqa
import six
from tempest.lib.cli import output_parser
import waiting

from stepler import base
from stepler import config
from stepler.third_party import steps_checker

__all__ = ['HeatCLISteps']


class HeatCLISteps(base.BaseSteps):
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
    def create_stack(self,
                     node,
                     name,
                     template_file=None,
                     template_url=None,
                     parameters=None,
                     check=True):
        """Step to create stack.

        Args:
            node (obj): os-fault node to execute command on it
            name (str): name of stack
            template_file (str, optional): path to yaml template
            template_url (str, optional): template url
            parameters (dict|None): parameters for template
            check (bool): flag whether check step or not

        Returns:
            dict: heat stack
        """
        err_msg = 'One of `template_file` or `template_url` should be passed.'
        assert_that(any([template_file, template_url]), is_(True), err_msg)
        cmd = 'heat stack-create ' + name
        if template_file:
            cmd += ' -f ' + template_file
        elif template_url:
            cmd += ' -u ' + template_url
        parameters = parameters or {}
        for key, value in parameters.items():
            cmd += ' --parameters {}={}'.format(key, value)
        cmd += ' --poll'
        stack_raw = self._client(node, cmd)
        stack_table = self._get_last_table(stack_raw['stdout'])
        stack = self._show_to_dict(stack_table)
        if check:
            self.check_stack_status(
                node,
                stack,
                config.HEAT_COMPLETE_CLI_STATUS,
                transit_statuses=[config.HEAT_IN_PROGRESS_STATUS],
                timeout=config.STACK_CREATION_TIMEOUT)

        return stack

    @steps_checker.step
    def check_stack_status(self,
                           node,
                           stack,
                           status,
                           transit_statuses=(),
                           timeout=0):
        """Verify step to check stack status.

        Args:
            node (obj): os-faults node to execute command on it
            stack (dict): heat stack to check its status
            status (str): expected stack status
            transit_statuses (iterable): allowed transit statuses
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
            AssertionError: if stack status is not equal `status`
        """
        stack_id = stack['id']

        def predicate():
            global stack
            cmd = "heat stack-show {}".format(stack_id)
            stack_raw = self._client(node, cmd)
            stack = self._show_to_dict(stack_raw['stdout'])
            return stack['stack_status'].lower() not in transit_statuses

        waiting.wait(predicate, timeout_seconds=timeout)
        assert_that(stack['stack_status'].lower(), equal_to(status.lower()))

    @steps_checker.step
    def get_stacks(self, node, check=True):
        """Step to retrieve stacks from heat.

        Args:
            node (obj): os-fault node
            check (bool): flag whether to check step or not

        Returns:
            list: stacks list
        """
        stacks_raw = self._client(node, 'heat stack-list')
        stacks = output_parser.listing(stacks_raw['stdout'])

        if check:
            assert_that(stacks, is_not(empty()))

        return stacks

    @steps_checker.step
    def delete_stack(self, node, stack, check=True):
        """Step to delete stack.

        Args:
            node (obj): os-fault node
            stack (obj): stack to delete
            check (bool): flag whether to check step or not

        Rasies:
            TimeoutExpired: if check was falsed after timeout
        """
        cmd = 'heat stack-delete {0[id]}'.format(stack)
        self._client(node, cmd)

        if check:
            self.check_stack_presence(
                node,
                stack,
                present=False,
                timeout=config.STACK_DELETING_TIMEOUT)

    @steps_checker.step
    def check_stack_presence(self, node, stack, present=True, timeout=0):
        """Check-step to check heat stack presence.

        Args:
            node (obj): os-fault node
            stack (obj): heat stack
            present (bool): flag to check is stack present or absent
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            return present == (stack['id'] in self._client(
                node, 'heat stack-list')['stdout'])

        waiting.wait(predicate, timeout_seconds=timeout)
