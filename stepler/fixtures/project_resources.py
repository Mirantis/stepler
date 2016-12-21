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
from keystoneauth1 import identity
from keystoneauth1 import session as _session
import pytest
from requests.packages import urllib3

from stepler import config
from stepler.third_party import context

__all__ = [
    'resource_manager',
    'admin_project_resources',
    'user_project_resources',
]


class ProjectResources(object):
    """Project resources structure."""
    def __init__(self, project, user, password):
        self.project = project
        self.user = user
        self.password = password

    @property
    def project_name(self):
        return self.project.name

    @property
    def username(self):
        return self.user.name


class ResourcesManager(object):
    """Resource manager class.

    The resource manager is used for creating new projects, getting
    keystone sessions using projects credentials and delete all created
    projects after tests.
    """

    def __init__(self, default_credentials):
        err_msg = "Environment variable OS_AUTH_URL is not defined"
        assert config.AUTH_URL, err_msg

        self.created_resources = {}
        self._default_credentials = default_credentials
        self._current_credentials = default_credentials

        # will be initialized if at least one resource is created
        # it is required for cleanup
        self._get_project_steps = None
        self._get_user_steps = None

    def _add_resource_to_created(self, resource):
        key = (resource.project.name, resource.user.name)
        self.created_resources[key] = resource

    def _delete_resources_from_create(self, resource):
        key = (resource.project.name, resource.user.name)
        if key in self.created_resources:
            del self.created_resources[key]

    @property
    def current_credentials(self):
        return self._current_credentials

    def set_current_credentials(self, credentials):
        """Function to set current credentials for session creation.

        Args:
            credentials (obj): object which have 'project_name',
                'username' and 'password' field (for example AttrDict or
                ProjectResources instance)
        """
        current = self._current_credentials
        if (credentials.project_name != current.project_name and
                credentials.username != current.username):
            new_credentials = attrdict.AttrDict()
            new_credentials.project_name = credentials.project_name
            new_credentials.username = credentials.username
            new_credentials.password = credentials.password

            self._current_credentials = new_credentials

    @context.context
    def set_current_credentials_context(self, project_resources):
        old_credentials = self._current_credentials
        self.set_current_credentials(project_resources)

        yield

        self.set_current_credentials(old_credentials)

    def get_session(
            self,
            username=None,
            password=None,
            project_name=None,
            auth_url=config.AUTH_URL,
            user_domain_name=config.USER_DOMAIN_NAME,
            project_domain_name=config.PROJECT_DOMAIN_NAME,
            cert=None):
        username = username or self.current_credentials.username
        password = password or self.current_credentials.password
        project_name = project_name or self.current_credentials.project_name

        if config.KEYSTONE_API_VERSION == 3:
            auth = identity.v3.Password(
                auth_url=auth_url,
                username=username,
                user_domain_name=user_domain_name,
                password=password,
                project_name=project_name,
                project_domain_name=project_domain_name)

        elif config.KEYSTONE_API_VERSION == 2:

            auth = identity.v2.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                tenant_name=project_name)

        else:
            raise ValueError("Unexpected keystone API version: {}".format(
                config.KEYSTONE_API_VERSION))

        if cert is None:
            urllib3.disable_warnings()
            return _session.Session(auth=auth, cert=cert, verify=False)
        else:
            return _session.Session(auth=auth, cert=cert)

    def build_project_resources(self,
                                get_project_steps,
                                get_role_steps,
                                get_user_steps,
                                project_name,
                                user_role,
                                user_name,
                                user_password):
        key = (project_name, user_name)
        if key in self.created_resources:
            return self.created_resources[key]

        if self._get_project_steps is None:
            self._get_project_steps = get_project_steps
            self._get_user_steps = get_user_steps

        project_steps = get_project_steps()
        role_steps = get_role_steps()
        user_steps = get_user_steps()

        project = project_steps.create_project(project_name)
        role = role_steps.get_role(name=user_role)
        user = user_steps.create_user(
            user_name=user_name, password=user_password)

        role_steps.grant_role(role, user, project=project)

        resources = ProjectResources(project, user, user_password)
        self._add_resource_to_created(resources)

        return resources

    def _delete_project_resources(self,
                                  project_resources):
        project_steps = self._get_project_steps()
        user_steps = self._get_user_steps()

        user_steps.delete_user(project_resources.user)
        project_steps.delete_project(project_resources.project)

        self._delete_resources_from_create(project_resources)

    def cleanup(self):
        self._current_credentials = self._default_credentials
        for _, resource in self.created_resources.items():
            self._delete_project_resources(resource)


@pytest.fixture(scope='session')
def resource_manager():
    """Function fixture to get resource manager instance.

    Yield:
        obj: ResourceManager instance
    """
    default_credentials = attrdict.AttrDict()
    default_credentials.project_name = config.PROJECT_NAME
    default_credentials.username = config.USERNAME
    default_credentials.password = config.PASSWORD

    _resource_manager = ResourcesManager(default_credentials)

    yield _resource_manager

    _resource_manager.cleanup()


@pytest.fixture(scope='session')
def admin_project_resources(resource_manager,
                            get_project_steps,
                            get_role_steps,
                            get_user_steps):
    """Function fixture to create project with admin user.

    This fixture also sets created admin resources as current
    for resource_manager.

    Args:
        resource_manager (obj): ResourcesManager instance
        get_project_steps (function): function to get project steps
        get_role_steps (function): function to get role steps
        get_user_steps (function): function to get user steps

    Yields:
        attrdict.AttrDict: created resources
    """
    project_name = config.ADMIN_PROJECT
    user_role = config.ROLE_ADMIN
    user_name = config.ADMIN_NAME
    user_password = config.ADMIN_PASSWD

    admin_project = resource_manager.build_project_resources(get_project_steps,
                                                             get_role_steps,
                                                             get_user_steps,
                                                             project_name,
                                                             user_role,
                                                             user_name,
                                                             user_password)

    old_credentials = resource_manager.current_credentials
    resource_manager.set_current_credentials(admin_project)

    yield admin_project

    resource_manager.set_current_credentials(old_credentials)


@pytest.fixture(scope='session')
def user_project_resources(resource_manager,
                           get_project_steps,
                           get_role_steps,
                           get_user_steps,):
    """Function fixture to create project with member user.

    Args:
        resource_manager (obj): ResourcesManager instance
        get_project_steps (function): function to get project steps
        get_role_steps (function): function to get role steps
        get_user_steps (function): function to get user steps

    Yields:
        attrdict.AttrDict: created resources
    """
    project_name = config.USER_PROJECT
    user_role = config.ROLE_MEMBER
    user_name = config.USER_NAME
    user_password = config.USER_PASSWD

    user_project = resource_manager.build_project_resources(get_project_steps,
                                                            get_role_steps,
                                                            get_user_steps,
                                                            project_name,
                                                            user_role,
                                                            user_name,
                                                            user_password)
    return user_project
