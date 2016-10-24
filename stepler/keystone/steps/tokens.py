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

from hamcrest import assert_that, has_key, has_items  # noqa

from stepler import base
from stepler.third_party import steps_checker

__all__ = [
    'TokenSteps'
]


class TokenSteps(base.BaseSteps):
    """Token steps."""

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
        if check and include_catalog:
            assert_that(token_validate, has_key('catalog'))

        return token_validate
