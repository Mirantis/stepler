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
                      equal_to, has_entry)  # noqa
from keystoneclient import exceptions
from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'UserSteps'
]


class UserSteps(BaseSteps):
    """User steps."""

    @step
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
            description (str): the newdescription of the user
            default_project (str or keystoneclient.v3.projects.Project):
                the new default project of the user
            kwargs: any other attribute provided will be passed to server

        Returns:
            keystoneclient.v3.users.User: new user
        """
        user = self._client.create(name=user_name,
                                   password=password,
                                   domain=domain,
                                   email=email,
                                   description=description,
                                   enabled=enabled,
                                   default_project=default_project,
                                   check=True,
                                   **kwargs)
        if check:
            self.check_user_presence(user)
            assert_that(user.name, equal_to(user_name))
            if domain == 'default':
                domain_id = domain
            else:
                domain_id = domain.id
            assert_that(user.domain_id, equal_to(domain_id))

        return user

    @step
    def delete_user(self, user, check=True):
        """Step to delete user.

        Args:
            user (object): user
            check (bool): flag whether to check step or not
        """
        self._client.delete(user.id)

        if check:
            self.check_user_presence(user, present=False)

    @step
    def get_user(self, name, domain='default', group=None, check=True):
        """Step to find user.

        Args:
            name (str) - user name
            domain (str or object): domain
            group (str or object): group

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

    @step
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

    @step
    def update_user(self, user, check=True, *args, **kwargs):
        """Step to update the user.

        Args:
            user (str or keystoneclient.v3.users.User): the user to be updated
                on the server
            name (str): the new name of the user
            domain (str or keystoneclient.v3.domains.Domain): the new domain
                of the user
            password (str): the new password of the user
            email (str): the new email of the user
            description (str): the newdescription of the user
            enabled (str): whether the user is enabled
            default_project (str or keystoneclient.v3.projects.Project):
                the new default project of the user

        kwargs: any other attribute provided will be passed to server

        Returns:
            keystoneclient.v3.users.User: the updated user returned from server

        :returns: the updated user returned from server.
        :rtype: :class:`keystoneclient.v3.users.User`
        """
        update_user = self._client.update(user=user, *args, **kwargs)

        if check:
            get_user = self._client.get(update_user)

            if not set(update_user.extra).issubset(get_user.to_dict()):
                raise ValueError('User was not updated')

        return update_user

    @step
    def check_user_presence(self, user, present=True, timeout=0):
        """Step to check user presence.

        Args:
            user (object): user
            present (bool): flag whether user should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check is failed after timeout
        """
        def predicate():
            try:
                self._client.get(user.id)
                return present
            except exceptions.NotFound:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
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
