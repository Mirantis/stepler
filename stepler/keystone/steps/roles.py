"""
----------
Role steps
----------
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

from hamcrest import equal_to
from keystoneclient import assert_that, exceptions, has_properties  # noqa

from stepler.base import BaseSteps
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'RoleSteps'
]


class RoleSteps(BaseSteps):
    """Role steps."""

    @steps_checker.step
    def create_role(self, role_name, check=True):
        """Step to create role.

        Args:
            role_name (str): the name of the role
            check (bool): flag whether to check step or not

        Returns:
            keystoneclient.v3.roles.Role: new role

        Raises:
            TimeoutExpired|AssertionError: if check was triggered to an error
        """
        role = self._client.create(role_name)

        if check:
            self.check_role_presence(role)
        return role

    @steps_checker.step
    def delete_role(self, role, check=True):
        """Step to delete role.

        Args:
            role (object): role
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired|AssertionError: if check was triggered to an error
        """
        self._client.delete(role.id)
        if check:
            self.check_role_presence(role, must_present=False)

    @steps_checker.step
    def get_role(self, check=True, *args, **kwgs):
        """Step to retrieve role.

        Args:
            check (bool): flag whether to check step or not
            kwgs could be: any other attribute provided will be passed to
                the server

        Returns:
            keystoneclient.v3.roles.Role: role
        """
        role = self._client.find(*args, **kwgs)
        if check:
            if args:
                assert_that(role, has_properties(args))
            if kwgs:
                assert_that(role, has_properties(kwgs))

        return role

    @steps_checker.step
    def grant_role(self,
                   role,
                   user=None,
                   group=None,
                   domain=None,
                   project=None,
                   check=True):
        """Step to grant role to user or group on domain or project.

        Args:
            role (str or obj): the role to be granted on the server
            user (str or obj): the specified user to have the role granted on
                a resource. Domain or project must be specified.
                User and group are mutually exclusive.
            group (str or obj): the specified group to have the role granted
                on a resource. Domain or project must be specified.
                User and group are mutually exclusive.
            domain (str or obj): the domain in which the role will be granted.
                Either user or group must be specified. Project and domain
                are mutually exclusive.
            project (str or obj): the project in which the role will be
                granted. Either user or group must be specified.
                Project and domain are mutually exclusive.
            check (bool): flag whether to check step or not

        Raises:
            NotFound: if check was triggered to an error
        """
        self._client.grant(role,
                           user=user,
                           group=group,
                           domain=domain,
                           project=project)
        if check:
            self.check_role_grant_status(role,
                                         user=user,
                                         group=group,
                                         domain=domain,
                                         project=project)

    @steps_checker.step
    def revoke_role(self,
                    role,
                    user=None,
                    group=None,
                    domain=None,
                    project=None,
                    check=True):
        """Step to revoke role from user or group on domain or project.

        Args:
            role (str or obj): the role to be revoked on the server
            user (str or obj): the specified user to have the role revoked on
                a resource. Domain or project must be specified.
                User and group are mutually exclusive.
            group (str or obj): revoke role grants for the specified group on
                a resource. Domain or project must be specified. User and
                group are mutually exclusive.
            domain (str or obj): revoke role grants on the specified domain.
                Either user or group must be specified. Project and domain
                are mutually exclusive.
            project (str or obj): revoke role grants on the specified project.
                Either user or group must be specified. Project and domain are
                mutually exclusive.
            check (bool): flag whether to check step or not

        Raises:
            NotFound: if check was triggered to an error
        """
        self._client.revoke(role,
                            user=user,
                            group=group,
                            domain=domain,
                            project=project)
        if check:
            self.check_role_grant_status(role,
                                         user=user,
                                         project=project,
                                         group=group,
                                         domain=domain,
                                         must_granted=False)

    @steps_checker.step
    def check_role_presence(self, role, must_present=True, timeout=0):
        """Check step that role is present.

        Args:
            role (str or obj): the role to be checked on the server
            must_present (bool): flag whether role should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check is triggered to an error after timeout
        """
        def _check_role_presence():
            try:
                self._client.get(role.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_role_presence, timeout_seconds=timeout)

    @steps_checker.step
    def check_role_grant_status(self,
                                role,
                                user=None,
                                group=None,
                                domain=None,
                                project=None,
                                must_granted=True,
                                timeout=0):
        """Check step if a user or group has a role on a domain or project.

        Args:
            role (str or obj): the role to be checked on a domain or project
            user (str or obj): check for role grants for the specified user on
                a resource. Domain or project must be specified. User and
                group are mutually exclusive.
            group (str or obj): check for role grants for the specified user on
                a resource. Domain or project must be specified. User and group
                are mutually exclusive.
                domain (str or obj): check for role grants on the specified
                domain. Either user or group must be specified. Project and
                domain are mutually exclusive.
            project (str or obj): check for role grants on the specified
                project. Either user or group must be specified. Project and
                domain are mutually exclusive.
            must_granted (bool): flag whether role should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check is triggered to an error after timeout
        """
        def _check_role_grant_status():
            try:
                self._client.check(role,
                                   user=user,
                                   group=group,
                                   domain=domain,
                                   project=project)
                is_granted = True
            except exceptions.NotFound:
                is_granted = False

            return expect_that(is_granted, equal_to(must_granted))

        waiter.wait(_check_role_grant_status, timeout_seconds=timeout)
