"""
--------------
Group fixtures
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

from stepler.keystone.steps import GroupSteps

__all__ = [
    'group_steps'
]


@pytest.fixture
def group_steps(keystone_client):
    """Fixture to get group steps.

    Args:
        keystone_client (object): instantiated keystone client

    Returns:
        stepler.keystone.steps.GroupSteps: instantiated group steps
    """
    return GroupSteps(keystone_client.groups)
