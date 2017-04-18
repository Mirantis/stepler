"""
-------------
Project tests
-------------
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

    @pytest.mark.idempotent_id('fc80ee7d-ce5a-45eb-b476-427990b3b61d')
    def test_create_project(self, projects_steps_ui):
        """**Scenario:** Verify that admin can create project.

        **Steps:**

        #. Create project using UI
        #. Delete project using UI
        """
        project_name = projects_steps_ui.create_project()
        projects_steps_ui.delete_project(project_name)
