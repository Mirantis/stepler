"""
--------------
Limit fixtures
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

import pytest

from stepler.nova.steps import NovaLimitSteps


@pytest.fixture
def nova_limit_steps(nova_client):
    """Callable function fixture to get nova limit steps.

    Args:
        nova_client (function): function to get nova client

    Returns:
        function: function to instantiated limit steps
    """
    return NovaLimitSteps(nova_client.limits)


@pytest.fixture
def nova_absolute_limits(nova_limit_steps):
    """Function fixture to get absolute limits.

    Args:
        nova_limit_steps (NovaLimitSteps): instantiated limit steps

    Returns:
        list: list of AbsoluteLimit objects
    """
    return nova_limit_steps.get_absolute_limits()
