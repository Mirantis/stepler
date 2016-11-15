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

from hamcrest import (assert_that, empty, equal_to, calling,
                      raises, is_not)  # noqa
from keystoneclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'ProjectSteps'
]


class ProjectSteps(BaseSteps):
    """Project steps."""

    @steps_checker.step
    def create_project(self, project_name, domain='default', check=True):
        """Step to create project.

        Args:
            project_name (str): project name
            domain (str or object): domain
            check (bool): flag whether to check step or not

        Returns:
            object: project
        """
        project = self._client.create(name=project_name, domain=domain)

        if check:
            self.check_project_presence(project)
            assert_that(project.name, equal_to(project_name))
            if hasattr(domain, 'id'):
                domain_id = domain.id
            else:
                domain_id = domain
            assert_that(project.domain_id, equal_to(domain_id))

        return project

    @steps_checker.step
    def delete_project(self, project, check=True):
        """Step to delete project.

        Args:
            project (object): keystone project
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.delete(project.id)

        if check:
            self.check_project_presence(project, must_present=False)

    @steps_checker.step
    def check_project_presence(self, project, must_present=True, timeout=0):
        """Check step that project is present.

        Args:
            project (object): keystone project to check presence status
            must_present (bool): flag whether image should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_project_presence():
            try:
                self._client.get(project.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_project_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_projects(self, check=True):
        """Step to get projects.

        Args:
            check (bool): flag whether to check step or not

        Returns:
            projects (list): list of projects

        Raises:
            AssertionError: if no projects found
        """
        projects = list(self._client.list())
        if check:
            assert_that(projects, is_not(empty()))

        return projects

    @steps_checker.step
    def get_current_project(self, session, check=True):
        """Step to get current project.

        Args:
            session (object): session object
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

    @steps_checker.step
    def check_get_projects_requires_authentication(self):
        """Step to check unauthorized request returns (HTTP 401)

        Raises:
            AssertionError: if check failed
        """
        exception_message = "The request you have made requires authentication"
        assert_that(calling(self.get_projects),
                    raises(exceptions.Unauthorized), exception_message)
