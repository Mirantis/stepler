"""
-------------
Project steps
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

from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'ProjectSteps'
]


class ProjectSteps(BaseSteps):
    """Project steps."""

    @step
    def create_project(self, project_name, domain, check=True):
        """Step to create project."""
        project = self._client.create(project_name, domain)

        if check:
            self.check_project_presence(project)

        return project

    @step
    def delete_project(self, project, check=True):
        """Step to delete project."""
        self._client.delete(project.id)

        if check:
            self.check_project_presence(project, present=False)

    @step
    def check_project_presence(self, project, present=True, timeout=0):
        """Check step that project is present."""
        def predicate():
            try:
                self._client.get(project.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def get_projects(self, check=True):
        """Step to get projects."""
        projects = list(self._client.list())
        if check:
            assert projects
        return projects
