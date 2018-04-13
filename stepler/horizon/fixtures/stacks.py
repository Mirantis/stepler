"""
-------------------
Fixtures for stacks
-------------------
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

from stepler.horizon import steps

__all__ = [
    'stacks_steps_ui'
]


@pytest.fixture
def stacks_steps_ui(stack_steps, login, horizon):
    """Functional fixture to get UI stacks steps.
    Args:
         stack_steps (StackSteps): instantiated stack steps
         login (None): should log in horizon before steps using
         horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.StacksSteps: instantiated stacks steps
    """
    return steps.StacksSteps(horizon)
