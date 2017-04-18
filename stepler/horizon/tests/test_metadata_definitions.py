"""
--------------------------
Metadata definitions tests
--------------------------
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
    """Tests for admin only."""

    @pytest.mark.idempotent_id('8b4d92cc-5b31-4fd7-80dc-935925f664f4')
    def test_create_namespace(self, namespaces_steps_ui):
        """**Scenario:** Verify that user can create namespace.

        **Steps:**

        #. Create namespace using UI
        #. Delete namespace using UI
        """
        namespace_name = namespaces_steps_ui.create_namespace()
        namespaces_steps_ui.delete_namespace(namespace_name)
