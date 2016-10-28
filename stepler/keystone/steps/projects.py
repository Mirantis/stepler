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

from hamcrest import assert_that, empty, equal_to  # noqa
from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'ProjectSteps'
]


class ProjectSteps(BaseSteps):
    """Project steps."""

    @step
    def create_project(self, project_name, domain='default', check=True):
        """Step to create project.

        Args:
            project_name (str): project name
            domain (str or object): domain
            check (bool): flag whether to check step or not

        Returns:
            object: project
        """
        project = self._client.create(project_name, domain)

        if check:
            self.check_project_presence(project)
            if hasattr(domain, 'id'):
                domain_id = domain.id
            else:
                domain_id = domain
            assert_that(project.domain_id, equal_to(domain_id))

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

    @step
    def get_current_project(self, session, check=True):
        """Step to get current project.

        Args:
            session (obj): session object
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if id of retrieved project is not equal to
            session project id

        Returns:
            object: project
        """
        project_id = session.get_project_id()
        project = self._client.get(project_id)
        if check:
            assert_that(project.id, equal_to(project_id))
        return project
