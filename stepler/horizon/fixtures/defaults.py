"""
---------------------
Fixtures for defaults
---------------------
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
    'defaults_steps_ui',
    'update_defaults'
]


@pytest.fixture
def defaults_steps_ui(login, horizon):
    """Fixture to get defaults steps.

    Args:
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.DefaultsSteps: instantiated UI defaults steps
    """
    return steps.DefaultsSteps(horizon)


@pytest.fixture
def update_defaults(defaults_steps_ui):
    """Callable fixture to update defaults.

    Args:
        defaults_steps_ui (DefaultsSteps): instantiated defaults steps

    Yields:
        function: function to update defaults
    """
    current_defaults = {}

    def _update_defaults(defaults):
        if not current_defaults:
            current_defaults.update(
                defaults_steps_ui.get_defaults(defaults))
        defaults_steps_ui.update_defaults(defaults)

    yield _update_defaults

    if current_defaults:
        defaults_steps_ui.update_defaults(current_defaults)
