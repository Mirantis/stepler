"""
---------
Ec2 steps
---------
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

from hamcrest import (assert_that, is_not, empty, has_properties,
                      equal_to)  # noqa
from keystoneclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'Ec2Steps'
]


class Ec2Steps(BaseSteps):
    """Ec2 credentials steps"""

    @steps_checker.step
    def list(self, user, check=True):
        """Step to list all ec2 credentials.

        Args:
            user (object): user
            check (bool): flag whether to check step or not

        Returns:
            keystoneclient.v3.ec2.Ec2: list of ec2 credentials

        Raises:
            AssertionError: if check failed
        """
        creds_list = self._client.list(user.id)
        if check:
            assert_that(creds_list, is_not(empty()))
        return creds_list

    @steps_checker.step
    def create(self, user, project, check=True):
        """Step to create EC2 credentials.

        Args:
            user (object): user
            project (object): project
            check (bool): flag whether to check step or not

        Returns:
            keystoneclient.v3.ec2.Ec2: ec2 credentials object

        Raises:
            AssertionError: if check failed
        """
        credentials = self._client.create(
            user_id=user.id, project_id=project.id)
        if check:
            assert_that(credentials,
                        has_properties(user_id=user.id, tenant_id=project.id))
        return credentials

    @steps_checker.step
    def delete(self, credentials, check=True):
        """Step to delete EC2 credentials.

        Args:
            credentials (keystoneclient.v3.ec2.Ec2): ec2 credentials object
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        self._client.delete(user_id=credentials.user_id,
                            access=credentials.access)
        if check:
            self.check_presence(credentials, must_present=False)

    @steps_checker.step
    def check_presence(self, credentials, must_present=True, timeout=0):
        """Step to check EC2 credentials presence.

        Args:
            credentials (keystoneclient.v3.ec2.Ec2): ec2 credentials object
            must_present (bool): flag whether credentials should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_presence():
            try:
                self._client.get(user_id=credentials.user_id,
                                 access=credentials.access)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_presence, timeout_seconds=timeout)
