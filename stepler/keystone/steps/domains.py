"""
------------
Domain steps
------------
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

from hamcrest import assert_that, is_not, empty, equal_to  # noqa
from keystoneclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party import steps_checker
from stepler.third_party.matchers import expect_that
from stepler.third_party import waiter

__all__ = [
    'DomainSteps'
]


class DomainSteps(BaseSteps):
    """Domain steps."""

    @steps_checker.step
    def get_domains(self, check=True):
        """Step to get domains.

        Args:
            check (bool): flag whether to check step or not

        Returns:
            list of objects: list of domains
        """
        domains = list(self._client.list())

        if check:
            assert_that(domains, is_not(empty()))
        return domains

    @steps_checker.step
    def get_domain(self, name, check=True):
        """Step to find domain.

        Args:
            name (str) - domain name

        Raises:
            NotFound: if domain does not exist

        Returns:
            object: domain
        """
        domain = self._client.find(name=name)

        if check:
            assert_that(domain.name, equal_to(name))

        return domain

    @steps_checker.step
    def create_domain(self, domain_name, check=True):
        """Step to create domain.

        Args:
            domain_name (str): domain name
            check (bool): flag whether to check step or not

        Returns:
            object: domain
        """
        domain = self._client.create(domain_name)

        if check:
            self.check_domain_presence(domain)
            assert_that(domain.name, equal_to(domain_name))

        return domain

    @steps_checker.step
    def delete_domain(self, domain, check=True):
        """Step to delete domain.

        Args:
            domain (object): domain
            check (bool): flag whether to check step or not
        """
        self._client.update(domain, enabled=False)
        self._client.delete(domain.id)

        if check:
            self.check_domain_presence(domain, must_present=False)

    @steps_checker.step
    def check_domain_presence(self, domain, must_present=True, timeout=0):
        """Step to check domain presence.

        Args:
            domain (object): domain
            present (bool): flag whether domain should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_domain_presence():
            try:
                self._client.get(domain.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_domain_presence, timeout_seconds=timeout)
