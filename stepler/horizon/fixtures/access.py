"""
----------------------------------
Fixtures to manipulate with access
----------------------------------
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
    'access_steps_ui',
]


@pytest.fixture
def access_steps_ui(horizon, login):
    """Fixture to get access steps.

    Args:
        horizon (Horizon): instantiated horizon web application
        login (None): should log in horizon before steps using
    """
    return steps.AccessSteps(horizon)
