"""
--------------------
Heat stacks fixtures
--------------------
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

import pytest

from stepler.heat import steps

__all__ = [
    'stack_steps',
    'create_stack',
    'stacks_cleanup',
]


@pytest.fixture
def stack_steps(heat_client):
    """Function fixture to get heat stack steps.

    Args:
        heat_client (object): initialized heat client

    Returns:
        stepler.heat.steps.StackSteps: initialized heat stack steps
    """
    return steps.StackSteps(heat_client.stacks)


@pytest.yield_fixture
def create_stack(stack_steps):
    """Fixture to create heat stack with options.

    Can be called several times during test.
    All created stacks will be deleted at teardown.

    Args:
        stack_steps (obj): initialized heat stack steps

    Returns:
        function: function to create heat stack
    """
    names = []

    def _create_stack(name, *args, **kwgs):
        names.append(name)
        stack = stack_steps.create(name, *args, **kwgs)
        return stack

    yield _create_stack

    if names:
        stacks = [stack for stack in stack_steps.get_stacks(check=False)
                  if stack.stack_name in names]
        for stack in stacks:
            stack_steps.delete(stack)


@pytest.yield_fixture
def stacks_cleanup(stack_steps):
    """Callable function fixture to clear created stacks after test.

    Args:
        stack_steps (obj): initialized heat stack steps
    """
    preserve_stacks_ids = set(
        x.id for x in stack_steps.get_stacks(check=False))
    yield
    for stack in stack_steps.get_stacks(check=False):
        if stack.id not in preserve_stacks_ids:
            stack_steps.delete(stack)
