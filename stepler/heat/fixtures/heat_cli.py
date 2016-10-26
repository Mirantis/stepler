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

import collections

import pytest

from stepler.heat import steps

__all__ = [
    'heat_cli_steps',
    'create_stack_cli',
]


@pytest.fixture
def heat_cli_steps(run_os_cli_command):
    """Function fixture to get heat CLI steps.

    Args:
        run_os_cli_command (function): function to call CLI command inside
        cloud

    Returns:
        stepler.heat.steps.StackSteps: initialized heat stack steps
    """
    return steps.HeatCLISteps(run_os_cli_command)


@pytest.yield_fixture
def create_stack_cli(heat_cli_steps):
    """Fixture to create heat stack with CLI with options.

    Can be called several times during test.
    All created stacks will be deleted at teardown.

    Args:
        heat_cli_steps (obj): initialized heat CLI steps

    Returns:
        function: function to create heat stack
    """
    names = []
    nodes = collections.deque(maxlen=1)

    def _create_stack(node, name, *args, **kwgs):
        names.append(name)
        nodes.append(node)
        stack = heat_cli_steps.create_stack(node, name, *args, **kwgs)
        return stack

    yield _create_stack

    if names:
        node = nodes.pop()
        stacks = [
            stack for stack in heat_cli_steps.get_stacks(
                node, check=False) if stack['stack_name'] in names
        ]
        for stack in stacks:
            heat_cli_steps.delete_stack(node, stack)
