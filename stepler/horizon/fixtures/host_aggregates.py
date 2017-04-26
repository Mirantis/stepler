"""
----------------------------
Fixtures for host aggregates
----------------------------
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
    'host_aggregates_steps_ui'
]


@pytest.fixture
def host_aggregates_steps_ui(login, horizon):
    """Fixture to get host aggregates steps.

    Args:
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.HostAggregatesSteps: instantiated UI
            host aggregates steps
    """
    return steps.HostAggregatesSteps(horizon)
