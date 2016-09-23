"""
Project fixtures.

@author: mshalamov@mirantis.com
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

from stepler.keystone.steps import ProjectSteps
from stepler.utils import generate_ids

__all__ = [
    'create_project',
    'project_steps',
    'project'
]


@pytest.fixture
def project_steps(keystone_client):
    """Fixture to get project steps."""
    return ProjectSteps(keystone_client.projects)


@pytest.yield_fixture
def create_project(project_steps):
    """Fixture to create project with options.

    Can be called several times during test.
    """
    projects = []

    def _create_project(project_name, domain):
        project = project_steps.create_project(project_name, domain)
        projects.append(project)
        return project

    yield _create_project

    for project in projects:
        project_steps.delete_project(project)


@pytest.fixture
def project(domain, create_project):
    """Fixture to create project with default options before test."""
    project_name = next(generate_ids('project'))
    return create_project(project_name, domain)
