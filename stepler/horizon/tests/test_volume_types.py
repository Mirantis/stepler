"""
-----------------
Volume type tests
-----------------
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


@pytest.mark.usefixtures('admin_only')
class TestAdminOnly(object):
    """Volume type tests are available for admin only."""

    @pytest.mark.idempotent_id('71441c2f-5b79-43de-88bf-c026cc1f5777')
    def test_volume_type_create(self, volume_type):
        """Verify that volume type can be created and deleted."""

    @pytest.mark.idempotent_id('3fb20c4a-7ab6-45e1-9f08-30ec942c4a89')
    def test_qos_spec_create(self, qos_spec):
        """Verify that QoS Spec can be created and deleted."""
