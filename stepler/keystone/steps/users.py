"""
User steps.

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

from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'UserSteps'
]


class UserSteps(BaseSteps):
    """User steps."""

    @step
    def create_user(self, user_name, password, check=True):
        """Step to create user."""
        user = self._client.create(user_name, password)

        if check:
            self.check_user_presence(user)

        return user

    @step
    def delete_user(self, user, check=True):
        """Step to delete user."""
        self._client.delete(user.id)

        if check:
            self.check_user_presence(user, present=False)

    @step
    def get_user(self, *args, **kwgs):
        """Step to find role."""
        return self._client.find(*args, **kwgs)

    @step
    def get_users(self, check=True):
        """Step to get projects."""
        users = list(self._client.list())
        if check:
            assert users
        return users

    @step
    def check_user_presence(self, user, present=True, timeout=0):
        """Check step that user is present."""
        def predicate():
            try:
                self._client.get(user.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)
