"""
------------------
Heat actions steps
------------------
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

from stepler import base
from stepler import config
from stepler.third_party import steps_checker

__all__ = ['ActionSteps']


class ActionSteps(base.BaseSteps):
    """Heat action steps"""

    @steps_checker.step
    def suspend(self, stack, stack_steps, check=True):
        """Step to suspend stack.

        Args:
            stack (obj): heat stack
            stack_steps (obj): instantiated stack steps
            check (bool, optional): flag whether check step or not

        Raises:
            AssertionError: if stack's stack_status is not
                config.STACK_STATUS_SUSPEND_COMPLETE after suspending
        """
        self._client.suspend(stack.id)
        if check:
            stack_steps.check_stack_status(
                stack,
                config.STACK_STATUS_SUSPEND_COMPLETE,
                transit_statuses=[config.STACK_STATUS_CREATE_COMPLETE],
                timeout=config.STACK_SUSPEND_TIMEOUT)
