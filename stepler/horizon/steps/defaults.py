"""
Horizon steps for defaults.

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

import pom

from .base import BaseSteps


class DefaultsSteps(BaseSteps):
    """Access & security steps."""

    def page_defaults(self):
        """Open access & security page."""
        return self._open(self.app.page_defaults)

    @pom.timeit('Step')
    def update_defaults(self, defaults, check=True):
        """Step to update defaults."""
        page_defaults = self.page_defaults()
        page_defaults.button_update_defaults.click()

        with page_defaults.form_update_defaults as form:
            for default_name, default_value in defaults.items():
                getattr(form, 'field_' + default_name).value = default_value
            form.submit()

        if check:
            self.close_notification('success')
            for default_name, default_value in defaults.items():
                assert getattr(page_defaults, 'label_' + default_name).value \
                    == str(default_value)

    @pom.timeit('Step')
    def get_defaults(self, defaults):
        """Step to get defaults."""
        result = {}
        page_defaults = self.page_defaults()
        for default_name in defaults:
            result[default_name] = getattr(
                page_defaults, 'label_' + default_name).value
        return result
