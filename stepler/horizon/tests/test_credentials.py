"""
Credentials tests.

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


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any one."""

    def test_download_rc_v2(self, api_access_steps):
        """Verify that one can download RCv2."""
        api_access_steps.download_rc_v2()

    def test_download_rc_v3(self, api_access_steps):
        """Verify that one can download RCv2."""
        api_access_steps.download_rc_v3()

    def test_view_credentials(self, api_access_steps):
        """Verify that one can view credentials."""
        api_access_steps.view_credentials()
