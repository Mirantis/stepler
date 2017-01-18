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

from hamcrest import assert_that, equal_to, is_in, is_not, empty, only_contains  # noqa

from stepler import base
from stepler import config
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
        response = self._client.stacks.create(
            stack_name=name,
            template=template,
            files=files,
            parameters=parameters)

        stack = self._client.stacks.get(response['stack']['id'])
        if check:
            self.check_status(
                stack,
                config.HEAT_COMPLETE_STATUS,
                transit_statuses=[config.HEAT_IN_PROGRESS_STATUS],
                timeout=config.STACK_CREATION_TIMEOUT)

        return stack

    def _get_property(self, stack, property_name, transit_values=(),
                      timeout=0):

        def _get_prop():
            stack.get()
            return waiter.expect_that(
                getattr(stack, property_name).lower(),
                is_not(is_in(transit_values)))

        waiter.wait(_get_prop, timeout_seconds=timeout)
        return getattr(stack, property_name)

    @steps_checker.step
    def check_status(self, stack, status, transit_statuses=(), timeout=0):
        """Verify step to check stack's `status` property.

        Args:
            stack (obj): heat stack to check its status
            status (str): expected stack status
            transit_statuses (iterable): allowed transit statuses
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """

        value = self._get_property(
            stack,
            'status',
            transit_values=transit_statuses,
            timeout=timeout)
        msg = getattr(stack, 'stack_status_reason', None)
        assert_that(value.lower(), equal_to(status.lower()), msg)

    @steps_checker.step
    def check_stack_status(self, stack, status, transit_statuses=(),
                           timeout=0):
        """Verify step to check stack's `stack_status` property.

        Args:
            stack (obj): heat stack to check its status
            status (str): expected stack status
            transit_statuses (iterable): allowed transit statuses
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was failed after timeout
        """

        def _check_stack_status():
            stack.get()
            value = self._get_property(
                stack,
                'stack_status',
                transit_values=transit_statuses,
                timeout=timeout)
            return waiter.expect_that(value.lower(), equal_to(status.lower()))

        waiter.wait(_check_stack_status, timeout_seconds=timeout)

    @steps_checker.step
    def get_stacks(self, check=True):
        """Step to retrieve stacks from heat.

        Args:
            check (bool): flag whether to check step or not

        Returns:
            list: stacks list
        """
        stacks = list(self._client.stacks.list())

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
            self.check_presence(stack,
                                must_present=False,
                                timeout=config.STACK_DELETING_TIMEOUT)

    @steps_checker.step
    def check_presence(self, stack, must_present=True, timeout=0):
        """Check-step to check heat stack presence.

        Args:
            stack (obj|str): heat stack object or id
            must_present (bool): flag to check is stack present or absent
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        if hasattr(stack, 'id'):
            stack = stack.id

        def _check_presence():
            stacks = list(self._client.stacks.list(id=stack))
            matcher = empty()
            if must_present:
                matcher = is_not(matcher)

            return waiter.expect_that(stacks, matcher)

        waiter.wait(_check_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_output(self, stack, output_key, check=True):
        """Step to get stack output by `output_key`.

        Args:
            stack (obj): stack object
            output_key (str): output key
            check (bool): flag whether check step or not

        Returns:
            dict: stack output

        Raises:
            AssertionError: if output is none or empty
        """
        output = stack.output_show(output_key)['output']

        if check:
            assert_that(output, is_not(None))
            assert_that(output, is_not(empty()))

        return output

    @steps_checker.step
    def update_stack(self, stack, template=None, parameters=None, check=True):
        """Step to update stack.

        Args:
            stack (obj): stack object
            template (str, optional): stack template on which to perform the
                operation. Default is None.
            parameters (dict, optional): stack parameters to update
            check (bool): flag whether check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        kwargs = {}
        if template is not None:
            kwargs['template'] = template
        if parameters is not None:
            kwargs['parameters'] = parameters
        self._client.stacks.update(stack_id=stack.id, **kwargs)

        if check:
            self.check_stack_status(stack,
                                    config.STACK_STATUS_UPDATE_COMPLETE,
                                    timeout=config.STACK_UPDATING_TIMEOUT)

    @steps_checker.step
    def get_stack_output_list(self, stack, check=True):
        """Step to get output list.

        Args:
            stack (obj): stack object
            check (bool): flag whether check step or not

        Returns:
            list: stack output list

        Raises:
            AssertionError: if check failed
        """
        output_list = self._client.stacks.output_list(stack.id)

        if check:
            assert_that(output_list, is_not(empty()))

        return output_list

    @steps_checker.step
    def check_output_list(self, output_list):
        """Step to check stack attributes in format: output_key - description.

        Args:
            output_list (dict): stack output list

        Raises:
            AssertionError: if check failed
        """
        assert_that(output_list['outputs'][0].keys(),
                    equal_to([u'output_key', u'description']))

    @steps_checker.step
    def suspend(self, stack, check=True):
        """Step to suspend stack.

        Args:
            stack (obj): heat stack
            check (bool, optional): flag whether check step or not

        Raises:
            AssertionError: if stack's stack_status is not
                config.STACK_STATUS_SUSPEND_COMPLETE after suspending
        """
        self._client.actions.suspend(stack.id)
        if check:
            self.check_stack_status(
                stack,
                config.STACK_STATUS_SUSPEND_COMPLETE,
                transit_statuses=[config.STACK_STATUS_CREATE_COMPLETE],
                timeout=config.STACK_SUSPEND_TIMEOUT)

    @steps_checker.step
    def get_events_list(self, stack, check=True):
        """Step to get stack's events list.

        Args:
            stack (obj): heat stack
            check (bool, optional): flag whether check step or not

        Raises:
            AssertionError: if events list is empty

        Returns:
            list: stack's events list
        """
        events = list(self._client.events.list(stack.id))
        if check:
            assert_that(events, is_not(empty()))
        return events

    @steps_checker.step
    def get_stack_template(self, stack, check=True):
        """Step to get stack's template.

        Args:
            stack (obj): heat stack
            check (bool, optional): flag whether check step or not

        Raises:
            AssertionError: if stack's template is empty

        Returns:
            dict: stack's template
        """
        template = self._client.stacks.template(stack.id)
        if check:
            assert_that(template, is_not(empty()))
        return template

    @steps_checker.step
    def get_stack_output_show(self, stack, output_key, check=True):
        """Step to get output show.

        Args:
            stack (obj): stack object
            output_key (str): the name of a stack output
            check (bool): flag whether check step or not

        Returns:
            dict: stack output

        Raises:
            AssertionError: if check failed
        """
        output_show = self._client.stacks.output_show(stack_id=stack.id,
                                                      output_key=output_key)
        if check:
            assert_that(output_show, is_not(empty()))
            assert_that(output_show['output']['output_key'],
                        equal_to(output_key))

        return output_show

    @steps_checker.step
    def check_output_show(self, output_show, expected_attr_values=None):
        """Step to check stack attributes.

        Args:
            output_show (dict): stack output
            expected_attr_values (dict|None): expected attribute values.
                If None, only check that elements of output_show are not empty.

        Raises:
            AssertionError: if check failed
        """
        if expected_attr_values:
            assert_that(output_show['output'], equal_to(expected_attr_values))
        else:
            assert_that(output_show['output'], only_contains(is_not(empty())))
