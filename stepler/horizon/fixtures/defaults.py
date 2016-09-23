"""
Fixtures for defaults.

@author: schipiga@mirantis.com
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

from stepler.horizon.steps import DefaultsSteps

__all__ = [
    'defaults_steps',
    'update_defaults'
]


@pytest.fixture
def defaults_steps(login, horizon):
    """Fixture to get defaults steps."""
    return DefaultsSteps(horizon)


@pytest.yield_fixture
def update_defaults(defaults_steps):
    """Callable fixture to update defaults."""
    current_defaults = {}

    def _update_defaults(defaults):
        if not current_defaults:
            current_defaults.update(
                defaults_steps.get_defaults(defaults))
        defaults_steps.update_defaults(defaults)

    yield _update_defaults

    if current_defaults:
        defaults_steps.update_defaults(current_defaults)
