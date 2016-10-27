"""
--------------------
Keystone token steps
--------------------
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

from hamcrest import assert_that, has_key, has_items, is_not, equal_to  # noqa
from keystoneclient import exceptions

from stepler import base
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'TokenSteps'
]


class TokenSteps(base.BaseSteps):
    """Token steps."""

    @steps_checker.step
    def revoke_token(self, token, check=True):
        """Step to revoke a token.

        Args:
            token (str): The token to be revoked.
            check (bool): flag whether to check step or not

        Returns:
            keystoneclient.access.AccessInfo: token
        """
        revoked_token = self._client.revoke_token(token=token)

        if check:
            self.check_token_is_revoked(revoked_token, must_revoked=False)

        return revoked_token

    @steps_checker.step
    def check_token_is_revoked(self, token, must_revoked=True, timeout=0):
        """Step to check if token is revoked.

        Args:
            token (str): The token to be checked.
            must_revoked (bool): flag whether volume should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was triggered to an error after timeout
        """
        def predicate():
            try:
                self.get_token_validate(token)
                is_revoked = True

            except exceptions.NotFound:
                is_revoked = False

            return expect_that(is_revoked, equal_to(must_revoked))

        waiter.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def get_token_data(self, token, include_catalog=True, check=True):
        """Step to fetch the data about a token from the identity server.

        Args:
            token (str): The ID of the token to be fetched
            include_catalog (bool): Whether the service catalog should be
                                    included in the response.
            check (bool): flag whether to check step or not

        Returns:
            dict: data about the token
        """
        token_data = self._client.get_token_data(
            token=token,
            include_catalog=include_catalog)

        if check:
            assert_that(token_data, has_key('token'))

        if check and include_catalog:
            assert_that(token_data['token'], has_key('catalog'))

        return token_data

    @steps_checker.step
    def get_token_validate(self, token, include_catalog=True, check=True):
        """Step to get validate a token.

        Args:
            token (str): The ID of the token to be fetched
            include_catalog (bool): Whether the service catalog should be
                                    included in the response.
            check (bool): flag whether to check step or not

        Returns:
            keystoneclient.access.AccessInfoV3: token access info
        """
        token_validate = self._client.validate(
            token=token,
            include_catalog=include_catalog)

        if check:
            assert_that(token_validate.keys(), has_items('methods',
                                                         'roles',
                                                         'auth_token',
                                                         'expires_at',
                                                         'project',
                                                         'version',
                                                         'user',
                                                         'audit_ids',
                                                         'issued_at'))
            if include_catalog:
                assert_that(token_validate, has_key('catalog'))

        return token_validate
