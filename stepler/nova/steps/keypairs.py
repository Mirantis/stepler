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

from hamcrest import assert_that, empty, equal_to, is_not  # noqa
from novaclient import exceptions as nova_exceptions

from stepler import base
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = [
    'KeypairSteps'
]


class KeypairSteps(base.BaseSteps):
    """Keypair steps."""

    @steps_checker.step
    def create_keypairs(self,
                        names=None,
                        count=1,
                        public_key=None,
                        check=True):
        """Step to create keypairs.

        Args:
            names (list, optional): Names of creating keypairs.
            count (int, optional): Count of creating keypairs, omitted
                if ``names`` is specified.
            public_key (str, optional): Existing public key to import.
            check (bool, optional): Flag whether to check step or not.

        Returns:
            list: Keypairs collection.

        Raises:
            TimeoutExpired | AssertionError: If check failed.
        """
        names = names or utils.generate_ids(count=count)

        keypairs = []
        for name in names:
            keypair = self._client.create(name, public_key=public_key)
            keypairs.append(keypair)

        if check:
            self.check_keypairs_presence(keypairs)

            for keypair in keypairs:
                if public_key is not None:
                    assert_that(keypair.public_key, equal_to(public_key))

        return keypairs

    @steps_checker.step
    def delete_keypairs(self,
                        keypairs,
                        check=True):
        """Step to delete keypairs.

        Args:
            keypairs (list): Keypairs to delete.
            check (bool, optional): Flag whether to check step or not.

        Raises:
            TimeoutExpired: If check failed.
        """
        for keypair in keypairs:
            self._client.delete(keypair.id)

        if check:
            self.check_keypairs_presence(keypairs, must_present=False)

    @steps_checker.step
    def get_keypairs(self,
                     name_prefix=None,
                     check=True):
        """Step to get keypairs.

        Args:
            name_prefix (str, optional): Name prefix to filter keypairs.
            check (bool, optional): Flag whether to check step or not.

        Returns:
            list: Keypairs collection.

        Raises:
            AssertionError: If check failed.
        """
        keypairs = list(self._client.list())

        if name_prefix:
            keypairs = [keypair for keypair in keypairs
                        if (keypair.name or '').startswith(name_prefix)]

        if check:
            assert_that(keypairs, is_not(empty()))

        return keypairs

    @steps_checker.step
    def check_keypairs_presence(self,
                                keypairs,
                                must_present=True,
                                keypair_timeout=0):
        """Step to check keypairs presence status.

        Args:
            keypairs (list): Keypairs to check.
            must_present (bool, optional): Flag whether keypairs must present
                or not.
            timeout (int, optional): Seconds to wait check result.

        Raises:
            TimeoutExpired: If check failed after timeout.
        """
        expected_presence = {keypair.id: must_present for keypair in keypairs}

        def predicate():
            actual_presence = {}
            for keypair in keypairs:

                try:
                    keypair.get()
                    actual_presence[keypair.id] = True

                except nova_exceptions.NotFound:
                    actual_presence[keypair.id] = False

            return expect_that(actual_presence, equal_to(expected_presence))

        timeout = len(keypairs) * keypair_timeout
        waiter.wait(predicate, timeout_seconds=timeout)
