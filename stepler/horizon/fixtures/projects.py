"""
Fixtures to manipulate with projects.

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

from stepler.horizon.steps import ProjectsSteps

from stepler.horizon.utils import AttrDict, generate_ids

__all__ = [
    'create_project',
    'project',
    'projects_steps'
]


@pytest.fixture
def projects_steps(horizon, login):
    """Fixture to get projects steps."""
    return ProjectsSteps(horizon)


@pytest.yield_fixture
def create_project(projects_steps):
    """Fixture to project with options.

    Can be called several times during test.
    """
    projects = []

    def _create_project(project_name):
        projects_steps.create_project(project_name)
        project = AttrDict(name=project_name)
        projects.append(project)
        return project

    yield _create_project

    for project in projects:
        projects_steps.delete_project(project.name)


@pytest.fixture
def project(create_project):
    """Fixture to create project with default options."""
    project_name = next(generate_ids('project'))
    return create_project(project_name)
