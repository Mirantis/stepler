"""
----------
User steps
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

from hamcrest import (assert_that, is_not, empty, only_contains,
                      equal_to, has_entries)  # noqa
from keystoneclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'UserSteps'
]


class UserSteps(BaseSteps):
    """User steps."""

    @steps_checker.step
    def create_user(self,
                    user_name,
                    password,
                    domain='default',
                    enabled=True,
                    email=None,
                    description=None,
                    default_project=None,
                    check=True,
                    **kwargs):
        """Step to create new user.

        Args:
            user_name (str): the new name of the user
            password (str): the new password of the user
            domain (str or keystoneclient.v3.domains.Domain): the new domain
                of the user
            enabled (str): whether the user is enabled
            email (str): the new email of the user
            description (str): the new description of the user
            default_project (str or keystoneclient.v3.projects.Project):
                the new default project of the user
            check (bool): flag whether to check step or not
            kwargs: any other attribute provided will be passed to server

        Returns:
            keystoneclient.v3.users.User: new user

        Raises:
            TimeoutExpired|AssertionError: if check was triggered to an error
        """
        user = self._client.create(name=user_name,
                                   password=password,
                                   domain=domain,
                                   email=email,
                                   description=description,
                                   enabled=enabled,
                                   default_project=default_project,
                                   **kwargs)
        if check:
            self.check_user_presence(user)
            assert_that(user.name, equal_to(user_name))

            if enabled:
                assert_that(user.enabled, equal_to(enabled))
            if email:
                assert_that(user.email, equal_to(email))
            if description:
                assert_that(user.description, equal_to(description))
            if default_project:
                assert_that(user.default_project, equal_to(default_project))
            if domain:
                if domain == 'default':
                    domain_id = domain
                else:
                    domain_id = domain.id
                assert_that(user.domain_id, equal_to(domain_id))
            if kwargs:
                assert_that(user.to_dict(), has_entries(kwargs))

        return user

    @steps_checker.step
    def delete_user(self, user, check=True):
        """Step to delete user.

        Args:
            user (object): user
            check (bool): flag whether to check step or not
        """
        self._client.delete(user.id)

        if check:
            self.check_user_presence(user, present=False)

    @steps_checker.step
    def get_user(self, name, domain='default', group=None, check=True):
        """Step to find user.

        Args:
            name (str) - user name
            domain (str or object): domain
            group (str or object): group
            check (bool): flag whether to check step or not

        Raises:
            NotFound: if user does not exist

        Returns:
            object: user
        """
        user = self._client.find(name=name, domain=domain, group=group)

        if check:
            assert_that(user.name, equal_to(name))
            domain_id = domain if domain == 'default' else domain.id
            assert_that(user.domain_id, equal_to(domain_id))
            # group is not checked because no user.group_id

        return user

    @steps_checker.step
    def get_users(self, domain='default', group=None, check=True):
        """Step to get users.

        Args:
            domain (str or object): domain
            group (str or object): group
            check (bool): flag whether to check step or not

        Returns:
            list of object: list of users
        """
        users = list(self._client.list(domain=domain, group=group))

        if check:
            if not group:
                assert_that(users, is_not(empty()))
            # group can be empty (no users)
            if len(users) > 0:
                domain_ids = [user.domain_id for user in users]
                if domain == 'default':
                    domain_id = domain
                else:
                    domain_id = domain.id
                assert_that(domain_ids, only_contains(domain_id))
                # group is not checked because no user.group_id

        return users

    @steps_checker.step
    def update_user(self, user, check=True, **kwargs):
        """Step to update the user.

        Args:
            user (str or keystoneclient.v3.users.User): the user to be updated
                on the server
            name (str): the new name of the user
            domain (str or keystoneclient.v3.domains.Domain): the new domain
                of the user
            password (str): the new password of the user
            email (str): the new email of the user
            description (str): the new description of the user
            enabled (str): whether the user is enabled
            default_project (str or keystoneclient.v3.projects.Project):
                the new default project of the user

        kwargs: any other attribute provided will be passed to server

        Raises:
            TimeoutExpired|AssertionError: if check was triggered to an error
        """
        updated_user = self._client.update(user=user, **kwargs)

        if check:
            # user.get()  https://bugs.launchpad.net/keystone/+bug/1637530
            # workaround
            user._add_details(updated_user._info)
            assert_that(user.to_dict(), has_entries(kwargs))

    @steps_checker.step
    def check_user_presence(self, user, must_present=True, timeout=0):
        """Step to check user presence.

        Args:
            user (object): user
            must_present (bool): flag whether user should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check is failed after timeout
        """
        def _check_user_presence():
            try:
                self._client.get(user.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_user_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_user_token(self, check=True):
        """Step to get user token.

        Args:
            check (bool): flag whether to check step or not

        Returns:
            token (str): user token
        """
        token = self._client.client.get_token()

        if check:
            assert_that(token, is_not(None))
        return token

    @steps_checker.step
    def add_user_to_group(self, user, group, check=True):
        """Step to add the specified user as a member of the specified group.

        Args:
            user (str or keystoneclient.v3.users.User): the user to be added
                to the group
            group (str or keystoneclient.v3.users.User): the group to put
                the user in
            check (bool): flag whether to check step or not

        Raises:
            NotFound: if check was triggered to an error
        """
        self._client.add_to_group(user=user, group=group)

        if check:
            self.check_user_in_group(user, group)

    @steps_checker.step
    def check_user_in_group(self,
                            user,
                            group,
                            must_present=True,
                            timeout=0):
        """Step to check if the user is a member of the group.

        Args:
            user (str or keystoneclient.v3.users.User): the user to be verified
                in the group
            group (str or keystoneclient.v3.users.User): the group to check
                the user in
            must_present (bool): flag whether group should present or no
            timeout (int): seconds to wait a result of check

        Returns:
            TimeoutExpired: if check is triggered to an error after timeout
        """
        def _check_user_in_group():
            try:
                user_is_in_group = self._client.check_in_group(user=user,
                                                               group=group)
            except exceptions.NotFound:
                user_is_in_group = False

            return expect_that(user_is_in_group, equal_to(must_present))

        waiter.wait(_check_user_in_group, timeout_seconds=timeout)
