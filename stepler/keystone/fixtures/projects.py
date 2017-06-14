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

import attrdict
import pytest

from stepler import config
from stepler.keystone import steps
from stepler.third_party import utils

__all__ = [
    'create_project',
    'get_project_steps',
    'project_steps',
    'get_current_project',
    'project',
    'current_project',
    'projects',
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


@pytest.fixture
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
    project_name = next(utils.generate_ids('project'))
    return create_project(project_name)


@pytest.fixture(scope="session")
def get_current_project(get_session, get_project_steps):
    """Callable session fixture to get current project.

    Args:
        get_session (function): function to get keystone session
        get_project_steps (function): function to get project steps

    Returns:
        function: function to get current project
    """
    def _get_current_project(**credentials):
        _session = get_session(**credentials)
        _project_steps = get_project_steps(**credentials)
        return _project_steps.get_current_project(_session)

    return _get_current_project


@pytest.fixture
def current_project(get_current_project):
    """Function fixture to get current project.

    Args:
        get_current_project (function): function to get current project

    Returns:
        obj: current project
    """
    return get_current_project()


@pytest.fixture
def projects(request, role_steps, create_project, create_user):
    """Function fixture to create different projects.

    By default count of projects equal to 2 , but if you want another count
    please add this quantity before your function.

    All created resources are to be deleted after test.

    Args:
        role_steps (obj): instantiated role steps
        create_project (function): function to create project
        create_user (function): function to create user

    Returns:
        attrdict.AttrDict: created resources
    """
    count = int(getattr(request, 'param', 2))
    base_name, = utils.generate_ids()
    resources = []
    admin_role = role_steps.get_role(name=config.ROLE_ADMIN)
    for i in range(count):
        project_resources = attrdict.AttrDict()
        name = "{}_{}".format(base_name, i)
        # Create project
        project = create_project(name)
        user = create_user(user_name=name, password=name)
        role_steps.grant_role(admin_role, user, project=project)
        credentials = dict(
            username=name, password=name, project_name=name)

        project_resources.credentials = credentials
        project_resources.project_id = project.id
        project_resources.name = name
        resources.append(project_resources)

    return attrdict.AttrDict(resources=resources)
