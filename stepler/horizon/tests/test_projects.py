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
from stepler import config
from stepler.third_party import utils


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

    @pytest.mark.idempotent_id('fada00f4-4a73-41ba-af56-6fd915414da9')
    def test_try_to_disable_current_project(self, projects_steps_ui):
        """**Scenario:** Verify that project can't disable itself.

        **Steps:**

        #. Try to disable current project
        """
        projects_steps_ui.check_project_cant_disable_itself()

    @pytest.mark.idempotent_id('b3c20e6e-b2f1-4c74-89e6-e72eaad1dfb8')
    def test_manage_project_members(self, project, admin_project_resources,
                                    projects_steps_ui):
        """**Scenario:** Check we can manage project members.

        **Setup:**

        #. Create project with API

        **Steps:**

        #. Manage project members using UI

        **Teardown:**

        #. Delete project with UI
        """
        projects_steps_ui.manage_project_members(project.name,
                                                 admin_project_resources)

    @pytest.mark.idempotent_id('83f706c1-6c1c-4a65-95e1-b045cd723fa1')
    def test_disable_enable_project(self, project, projects_steps_ui):
        """**Scenario:** Disable and enable created project.

        **Setup:**

        #. Create project with API

        **Steps:**

        #. Disable created project with UI
        #. Enable it using UI

        **Teardown:**

        #. Delete project via API
        """
        projects_steps_ui.toggle_project(project, enable=False)
        projects_steps_ui.toggle_project(project, enable=True)

    @pytest.mark.idempotent_id('9acd7607-d72f-4e8c-9b13-1a0728d56975')
    def test_switch_projects(self, admin_project_resources, project,
                             projects_steps_ui, overview_steps_ui,
                             security_groups_steps_ui):
        """**Scenario:** Check resources in different projects.

        **Setup:**

        #. Create project with API

        **Steps:**

        #. Check overview of base project before creating resource
        #. Create security group for base project using UI
        #. Check that quantity of resource for base project has been grown
        #. Manage project members using UI
        #. Switch on created project
        #. Check overview before creating resource
        #. Create security group using UI
        #. Check that quantity of resource has been grown

        **Teardown:**

        #. Delete project via API
        """
        quantity_resource_base = overview_steps_ui.get_used_resource_overview(
            resource_name=config.RESOURCE_NAME_SECURITY)
        security_groups_steps_ui.create_security_group()
        overview_steps_ui.check_resource_item_changed(
            resource_name=config.RESOURCE_NAME_SECURITY,
            resource_before_creating=quantity_resource_base)
        projects_steps_ui.manage_project_members(project.name,
                                                 admin_project_resources)
        projects_steps_ui.switch_project(project.name)
        quantity_resource = overview_steps_ui.get_used_resource_overview(
            resource_name=config.RESOURCE_NAME_SECURITY)
        security_groups_steps_ui.create_security_group()
        overview_steps_ui.check_resource_item_changed(
            resource_name=config.RESOURCE_NAME_SECURITY,
            resource_before_creating=quantity_resource)

    @pytest.mark.idempotent_id('f2d50cf8-62f5-11e7-a478-5404a69126b9')
    def test_update_project_name(self, project, projects_steps_ui):
        """**Scenario:** Check that project can be deleted after update name.

        **Setup:**

        #. Create project with API

        **Steps:**

        #. Update project name

        **Teardown:**

        #. Delete project via API
        """
        new_project_name = next(utils.generate_ids())
        projects_steps_ui.update_project_name(project.name, new_project_name)
