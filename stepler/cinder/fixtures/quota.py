"""
---------------
 Cinder quota fixtures
---------------
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

from stepler.cinder import steps

__all__ = [
    'cinder_quota_steps',
]


@pytest.fixture
def cinder_quota_steps(cinder_client):
    """Function fixture to get cinder quota steps.

    Args:
        cinder_client (object): instantiated cinder client

    Returns:
        stepler.cinder.steps.CinderQuotaSteps: instantiated quota steps
    """
    return steps.CinderQuotaSteps(cinder_client.quotas)
