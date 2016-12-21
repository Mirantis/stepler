"""
--------------------------
Project resources fixtures
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

import attrdict
import pytest

from stepler import config
from stepler.third_party import context

__all__ = [
    'admin_project_resources',
    'user_project_resources',
    'create_project_resources',
]


@pytest.fixture(scope='session')
def admin_project_resources(create_project_resources,
                            os_credentials):
    """Fixture to create project with admin user.

    This fixture also updates os_credentials with values of
    the created project and admin user.

    Args:
        create_project_resources (function): function to create
            project resources
        os_credentials (AttrDict): data structure with credentials
            to be changed

    Yields:
        attrdict.AttrDict: created resources
    """
    project_name = config.ADMIN_PROJECT
    user_role = config.ROLE_ADMIN
    user_name = config.ADMIN_NAME
    user_password = config.ADMIN_PASSWD

    with create_project_resources(project_name, user_role, user_name,
                                  user_password) as admin_resources:
        with os_credentials.change(project_name, user_name, user_password):
            yield admin_resources


@pytest.fixture(scope='session')
def user_project_resources(create_project_resources):
    """Fixture to create project with member user.

    Args:
        create_project_resources (function): function to create
            project resources
        os_credentials (AttrDict): data structure with credentials
            to be changed

    Yields:
        attrdict.AttrDict: created resources
    """
    project_name = config.USER_PROJECT
    user_role = config.ROLE_MEMBER
    user_name = config.USER_NAME
    user_password = config.USER_PASSWD

    with create_project_resources(project_name, user_role, user_name,
                                  user_password) as user_resources:
        yield user_resources


@pytest.fixture(scope='session')
def create_project_resources(get_project_steps,
                             get_user_steps,
                             get_role_steps):
    """Callable session fixture to create project resources.

    This fixture creates project, user and grants required role
    on project to this user.

    Args:
        get_project_steps (function): function to get instantiated project
            steps
        get_user_steps (function): function to get instantiated user steps
        get_role_steps (function): function to get instantiated role steps

    Yields:
        attrdict.AttrDict: created resources which contain project,
            user, role and password
    """
    @context.context
    def _create_project_resources(project_name, user_role, user_name,
                                  user_password):
        project_resources = _build_project_resources(get_project_steps,
                                                     get_user_steps,
                                                     get_role_steps,
                                                     project_name,
                                                     user_role,
                                                     user_name,
                                                     user_password)
        yield project_resources

        _delete_project_resources(get_project_steps,
                                  get_user_steps,
                                  project_resources)

    return _create_project_resources


def _build_project_resources(get_project_steps,
                             get_user_steps,
                             get_role_steps,
                             project_name,
                             user_role,
                             user_name,
                             user_password):
    project_steps = get_project_steps()
    role_steps = get_role_steps()
    user_steps = get_user_steps()

    project = project_steps.create_project(project_name)
    role = role_steps.get_role(name=user_role)
    user = user_steps.create_user(
        user_name=user_name, password=user_password)

    role_steps.grant_role(role, user, project=project)

    project_resources = attrdict.AttrDict()
    project_resources.project = project
    project_resources.role = role
    project_resources.user = user
    project_resources.user_password = user_password

    return project_resources


def _delete_project_resources(get_project_steps,
                              get_user_steps,
                              project_resources):
    project_steps = get_project_steps()
    user_steps = get_user_steps()

    user_steps.delete_user(project_resources.user)
    project_steps.delete_project(project_resources.project)
