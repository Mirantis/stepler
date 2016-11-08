"""
-------------
Keypair steps
-------------
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

from hamcrest import assert_that, equal_to  # noqa
from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party import steps_checker

__all__ = [
    'KeypairSteps'
]


class KeypairSteps(BaseSteps):
    """Keypair steps."""

    @steps_checker.step
    def create_keypair(self, keypair_name, public_key=None, check=True):
        """Step to create keypair.

        Args:
            keypair_name (str): name for the keypair to create
            public_key (str): existing public key to import

        Returns:
            keypair (object): keypair

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        keypair = self._client.create(keypair_name, public_key=public_key)

        if check:
            self.check_keypair_presence(keypair)
            if public_key is not None:
                assert_that(keypair.public_key, equal_to(public_key))

        return keypair

    @steps_checker.step
    def delete_keypair(self, keypair, check=True):
        """Step to delete keypair.

        Args:
            keypair (object): key to delete.
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.delete(keypair.id)

        if check:
            self.check_keypair_presence(keypair, present=False)

    @steps_checker.step
    def check_keypair_presence(self, keypair, present=True, timeout=0):
        """Verify step to check keypair is present.

        Args:
            keypair (class or its ID): key to check.
            present (bool): flag whether image should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def predicate():
            try:
                self._client.get(keypair.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)
