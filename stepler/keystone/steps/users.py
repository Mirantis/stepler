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

from hamcrest import assert_that, is_not, empty
from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'UserSteps'
]


class UserSteps(BaseSteps):
    """User steps."""

    @step
    def create_user(self, user_name, password, domain='default', check=True):
        """Step to create user.

        Args:
            user_name (str): user name
            password (str): password
            domain (str or object): domain
            check (bool): flag whether to check step or not

        Returns:
            object: user
        """
        user = self._client.create(name=user_name, password=password,
                                   domain=domain)
        if check:
            self.check_user_presence(user)

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
    def get_user(self, name, domain='default', group=None):
        """Step to find user.

        Args:
            name (str) - user name
            domain (str or object): domain
            group (str or object): group

        Raises:
            NotFound: if such user does not exist

        Returns:
            object: user
        """
        return self._client.find(name=name, domain=domain, group=group)

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
            assert_that(users, is_not(empty()))
        return users

    @step
    def check_user_presence(self, user, present=True, timeout=0):
        """Step to check user presence.

        Args:
            user (object): user
            present (bool): flag if user must exist or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutError: if check is failed after timeout
        """
        def predicate():
            try:
                self._client.get(user.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)
