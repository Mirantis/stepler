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
        """Step to create keypair.

        Args:
            keypair_name (str): name for the keypair to create
            public_key (str): existing public key to import

        Returns:
            keypair (object): keypair

        Raises:
            TimeoutExpired: if check failed after timeout
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
        """Step to delete keypair.

        Args:
            keypair (object): key to delete.
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        for keypair in keypairs:
            self._client.delete(keypair.id)

        if check:
            self.check_keypairs_presence(keypairs, must_present=False)

    @steps_checker.step
    def get_keypairs(self, name_prefix=None, check=True):
        """Step to get keypairs.

        Args:
            name_prefix (str): name prefix to filter keypairs
            check (bool): flag whether to check step or not

        Returns:
            list: keypairs collection

        Raises:
            AssertionError: if check failed
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
        """Step to check keypair is present.

        Args:
            keypair (class or its ID): key to check.
            present (bool): flag whether image should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
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
