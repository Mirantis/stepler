"""
----------------
Heat stack steps
----------------
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

from hamcrest import assert_that, equal_to, is_not, empty  # noqa
import waiting

from stepler import base
from stepler import config
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ['StackSteps']


class StackSteps(base.BaseSteps):
    """Heat stack steps."""

    @steps_checker.step
    def create(self, name, template, parameters=None, files=None, check=True):
        """Step to create stack.

        Args:
            name (str): name of stack
            template (str): yaml template content for create stack from
            parameters (dict|None): parameters for template
            files (dict|None): in case if template uses file as reference
                e.g: "type: volume_with_attachment.yaml"
            check (bool): flag whether check step or not

        Returns:
            object: heat stack
        """
        parameters = parameters or {}
        files = files or {}
        response = self._client.create(
            stack_name=name,
            template=template,
            files=files,
            parameters=parameters)

        stack = self._client.get(response['stack']['id'])
        if check:
            self.check_status(
                stack,
                config.HEAT_COMPLETE_STATUS,
                transit_statuses=[config.HEAT_IN_PROGRESS_STATUS],
                timeout=config.STACK_CREATION_TIMEOUT)

        return stack

    @steps_checker.step
    def check_status(self, stack, status, transit_statuses=(), timeout=0):
        """Verify step to check stack status.

        Args:
            stack (obj): heat stack to check its status
            status (str): expected stack status
            transit_statuses (iterable): allowed transit statuses
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def predicate():
            stack.get()
            return stack.status.lower() not in transit_statuses

        waiting.wait(predicate, timeout_seconds=timeout)
        assert_that(stack.status.lower(), equal_to(status.lower()))

    @steps_checker.step
    def get_stacks(self, check=True):
        """Step to retrieve stacks from heat.

        Args:
            check (bool): flag whether to check step or not
        Returns:
            list: stacks list
        """
        stacks = list(self._client.list())

        if check:
            assert_that(stacks, is_not(empty()))

        return stacks

    @steps_checker.step
    def delete(self, stack, check=True):
        """Step to delete stack.

        Args:
            stack (obj): stack to delete
            check (bool): flag whether to check step or not
        Raises:
            TimeoutExpired: if check failed after timeout
        """
        stack.delete()

        if check:
            self.check_presence(
                stack, present=False, timeout=config.STACK_DELETING_TIMEOUT)

    @steps_checker.step
    def check_presence(self, stack, present=True, timeout=0):
        """Check-step to check heat stack presence.

        Args:
            stack (obj|str): heat stack object or id
            present (bool): flag to check is stack present or absent
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        stack_id = getattr(stack, 'id', stack)

        def predicate():
            try:
                next(self._client.list(id=stack_id))
                return present
            except StopIteration:
                return not present

        waiting.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def get_output(self, stack, output_key):
        """Step to get stack output by `output_key`.

        Args:
            stack (obj): stack object
            output_key (str): output key

        Returns:
            dict: stack output
        """
        stack.get()
        return stack.output_show(output_key)['output']

    @steps_checker.step
    def update_stack(self, stack, template, check=True):
        """Step to update stack.

        Args:
            stack (obj): stack object
            template (str): stack template on which to perform the operation
            check (bool): flag whether check step or not

        Raises:
            TimeoutExpired: if check was failed
        """
        self._client.update(stack_id=stack.id, template=template)

        if check:
            self.check_stack_status(stack,
                                    config.STACK_STATUS_UPDATE_COMPLETE,
                                    timeout=config.STACK_UPDATING_TIMEOUT)

    @steps_checker.step
    def check_stack_status(self, stack, status, timeout=0):
        """Step to check stack status.

        Args:
            stack (obj): stack object
            status (str): stack status name to check
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def predicate():
            stack.get()
            return expect_that(stack.stack_status.lower(),
                               equal_to(status.lower()))

        waiter.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def get_stack_output_list(self, stack, check=True):
        """Step to get output list.

        Args:
            stack (obj): stack object
            check (bool): flag whether check step or not

        Returns:
            list: stack output list

        Raises:
            AssertionError: if check was failed
        """
        output_list = self._client.output_list(stack.id)

        if check:
            assert_that(output_list, is_not(empty()))

        return output_list

    @steps_checker.step
    def check_output_list(self, output_list):
        """Step to check stack attributes in format: output_key - description.
        Args:
            output_list (dict): stack output list

        Raises:
            AssertionError: if check was failed
        """
        assert_that(output_list['outputs'][0].keys(),
                    equal_to([u'output_key', u'description']))
