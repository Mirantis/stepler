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

from stepler import config
from stepler.heat import steps
from stepler.third_party import utils

__all__ = [
    'stack_steps',
    'create_stack',
    'stacks_cleanup',
    'empty_stack',
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

    It stores ids of all stacks before test and remove all new stacks after
    test done.

    Args:
        stack_steps (obj): initialized heat stack steps
    """
    preserve_stacks_ids = set(
        stack.id for stack in stack_steps.get_stacks(check=False))

    yield

    for stack in stack_steps.get_stacks(check=False):
        if (stack.id not in preserve_stacks_ids and
                stack.stack_name.startswith(config.STEPLER_PREFIX)):
            stack_steps.delete(stack)


@pytest.fixture
def empty_stack(create_stack, read_heat_template):
    """Function fixture to create empty heat stack.

    Args:
        create_stack (function): fixture to create stack
        read_heat_template (function): fixture to read template

    Returns:
        obj: created stack
    """
    name = next(utils.generate_ids('stack'))
    template = read_heat_template('empty_heat_template')
    return create_stack(
        name,
        template=template,
        parameters={
            'param': 'string',
        })
