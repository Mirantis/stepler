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

from hamcrest import assert_that, is_not, empty  # noqa

from stepler.base import BaseSteps
from stepler.third_party import steps_checker

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

        Raises:
            TimeoutExpired|AssertionError: if check failed
        """
        creds_list = self._client.list(user.id)
        if check:
            assert_that(creds_list, is_not(empty()))
        return creds_list
