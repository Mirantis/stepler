"""
-----------
Group steps
-----------
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
                      equal_to)  # noqa
from keystoneclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'GroupSteps'
]


class GroupSteps(BaseSteps):
    """Group steps."""

    @steps_checker.step
    def create_group(self,
                     name,
                     domain=None,
                     description=None,
                     check=True):
        """Step to create a group.

        Args:

            name (str): the name of the group
            domain (str or class `keystoneclient.v3.domains.Domain`):
                the domain of the group
            description (str): a description of the group

        Returns:
            keystoneclient.v3.groups.Group: the created group returned
            from server

        Raises:
            TimeoutExpired|AssertionError: if check was triggered to an error
        """
        group = self._client.create(name=name,
                                    domain=domain,
                                    description=description)
        if check:
            self.check_group_presence(group, must_present=True)
            assert_that(group.name, equal_to(name))

            if domain:
                assert_that(group.domain, equal_to(domain))
            if description:
                assert_that(group.description, equal_to(description))

        return group

    @steps_checker.step
    def delete_group(self, group, check=True):
        """Step to delete group.

        Args:
            group (object): the group to be deleted on the server.

        Returns:
            requests.models.Response: response object with 204 status.
        """
        self._client.delete(group)

        if check:
            self.check_group_presence(group, must_present=False)

    @steps_checker.step
    def check_group_presence(self, group, must_present=True, timeout=0):
        """Step to check group presence.

        Args:
            group (object): the keystone group to be checked
            must_present (bool): flag whether user should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check is triggered to an error after timeout
        """
        def predicate():
            try:
                self._client.get(group)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def get_groups(self, domain='default', check=True):
        """Step to get groups.

        Args:
            domain (str or object): domain
            check (bool): flag whether to check step or not

        Returns:
            list of objects: list of groups
        """
        groups = list(self._client.list(domain=domain))

        if check:
            assert_that(groups, is_not(empty()))
            domain_ids = [group.domain_id for group in groups]
            if domain == 'default':
                domain_id = domain
            else:
                domain_id = domain.id
            assert_that(domain_ids, only_contains(domain_id))

        return groups

    @steps_checker.step
    def get_group(self, name, domain='default', check=True):
        """Step to find group.

        Args:
            name (str) - group name
            domain (str or object): domain

        Raises:
            NotFound: if group does not exist

        Returns:
            object: group
        """
        group = self._client.find(name=name, domain=domain)

        if check:
            assert_that(group.name, equal_to(name))
            if domain == 'default':
                domain_id = domain
            else:
                domain_id = domain.id
            assert_that(group.domain_id, equal_to(domain_id))

        return group
