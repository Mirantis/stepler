"""
---------------------
Fixtures for settings
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
    'settings_steps_ui',
    'update_settings'
]


@pytest.fixture
def settings_steps_ui(login, horizon):
    """Get settings steps.

    Args:
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.SettingsSteps: instantiated settings steps
    """
    return steps.SettingsSteps(horizon)


@pytest.fixture
def update_settings(settings_steps_ui):
    """Update settings.

    Args:
        settings_steps (SettingsSteps): instantiated settings steps

    Yields:
        function: function to update user settings
    """
    current_settings = {}

    def _update_settings(lang=None, timezone=None, items_per_page=None,
                         instance_log_length=None):
        current_settings.update(settings_steps_ui.get_current_settings())
        settings_steps_ui.update_settings(lang, timezone, items_per_page,
                                          instance_log_length)

    yield _update_settings

    if current_settings:
        settings_steps_ui.update_settings(**current_settings)
