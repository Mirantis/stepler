"""
----------------
Project fixtures
----------------
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

from stepler.keystone import steps
from stepler.third_party.utils import generate_ids

__all__ = [
    'create_project',
    'get_project_steps',
    'project_steps',
    'project',
    'current_project',
]


@pytest.fixture(scope="session")
def get_project_steps(get_keystone_client):
    """Callable session fixture to get project steps.

    Args:
        get_keystone_client (function): function to get keystone client.

    Returns:
        function: function to get project steps.
    """
    def _get_steps(**credentials):
        return steps.ProjectSteps(get_keystone_client(**credentials).projects)

    return _get_steps


@pytest.fixture
def project_steps(get_project_steps):
    """Function fixture to get project steps.

    Args:
        get_project_steps (function): function to get project steps

    Returns:
        ProjectSteps: instantiated project steps.
    """
    return get_project_steps()


@pytest.yield_fixture
def create_project(project_steps):
    """Fixture to create project with options.

    Can be called several times during test.
    """
    projects = []

    def _create_project(*args, **kwargs):
        project = project_steps.create_project(*args, **kwargs)
        projects.append(project)
        return project

    yield _create_project

    for project in projects:
        project_steps.delete_project(project)


@pytest.fixture
def project(create_project):
    """Fixture to create project with default options before test."""
    project_name = next(generate_ids('project'))
    return create_project(project_name)


@pytest.fixture
def current_project(session, project_steps):
    """Function fixture to get current project.

    Args:
        session (obj): instantiated keystone session
        project_steps (obj): instantiated project steps

    Returns:
        obj: current project
    """
    return project_steps.get_current_project(session)
