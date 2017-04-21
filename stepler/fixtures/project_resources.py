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
from stepler.third_party import utils

__all__ = [
    'create_user_with_project',
    'admin_project_resources',
    'user_project_resources',
]


@pytest.fixture(scope='session')
def create_user_with_project(credentials,
                             get_project_steps,
                             get_user_steps,
                             get_role_steps):
    """Callable fixture to create project with user.

    This function creates project, user and role (if role doesn't exist)
    and adds project_name, username and password to known credentials.
    As result this credentials can be retrieved using ``credentials``
    fixture and alias.

    Args:
        credentials (object): CredentialsManager instance
        get_project_steps (function): function to get project steps
        get_role_steps (function): function to get role steps
        get_user_steps (function): function to get user steps

    Yields:
        attrdict.AttrDict: created resources
    """

    @context.context
    def _create_user_with_project(creds_alias,
                                  username=None,
                                  password=None,
                                  project_name=None,
                                  role_type=None):
        username = username or next(utils.generate_ids('user'))
        password = password or next(utils.generate_ids('password'))
        project_name = project_name or next(utils.generate_ids('project'))

        role_steps = get_role_steps()

        if role_type:
            role = role_steps.get_role(name=role_type)
        else:
            role = role_steps.create_role()

        project = get_project_steps().create_project(project_name)
        user = get_user_steps().create_user(user_name=username,
                                            password=password,
                                            default_project=project)
        role_steps.grant_role(role, user, project=project)

        resources = attrdict.AttrDict({'alias': creds_alias,
                                       'user': user,
                                       'password': password,
                                       'project': project,
                                       'role': role})
        creds = {
            'username': username,
            'password': password,
            'project_name': project_name,
        }
        credentials.set(creds_alias, creds)

        yield resources

        get_user_steps().delete_user(resources.user)
        get_project_steps().delete_project(resources.project)
        if not role_type:
            get_role_steps().delete_role(role)

    return _create_user_with_project


@pytest.fixture(scope='session')
def admin_project_resources(credentials, create_user_with_project):
    """Function fixture to create project with admin user.

    This fixture also sets created admin resources as current
    for resource_manager.

    Args:
        credentials (object): CredentialsManager instance
        create_user_with_project (function): function to create
            project resources

    Yields:
        attrdict.AttrDict: created resources
    """
    creds_alias = 'admin'
    admin_credentials = {
        'username': config.ADMIN_NAME,
        'password': config.ADMIN_PASSWD,
        'project_name': config.ADMIN_PROJECT,
        'role_type': config.ROLE_ADMIN
    }
    with create_user_with_project(creds_alias,
                                  **admin_credentials) as resource:
        with credentials.change(creds_alias):
            yield resource


@pytest.fixture(scope='session')
def user_project_resources(create_user_with_project):
    """Function fixture to create project with member user.

    Args:
        create_user_with_project (function): function to create
            project resources

    Yields:
        attrdict.AttrDict: created resources
    """
    creds_alias = 'user'
    user_credentials = {
        'username': config.USER_NAME,
        'password': config.USER_PASSWD,
        'project_name': config.USER_PROJECT,
        'role_type': config.ROLE_MEMBER
    }

    with create_user_with_project(creds_alias,
                                  **user_credentials) as resource:
        yield resource
