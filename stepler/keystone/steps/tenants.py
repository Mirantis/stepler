"""
-------------
Tenant steps
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

from hamcrest import (assert_that, empty, equal_to, calling,
                      raises, is_not)  # noqa
from keystoneclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'TenantSteps'
]


class TenantSteps(BaseSteps):
    """Tenant steps."""

    @steps_checker.step
    def create_tenant(self, tenant_name, domain='default', check=True):
        """Step to create tenant.

        Args:
            tenant_name (str): tenant name.
            domain (str or object): domain.
            check (bool): flag whether to check step or not.

        Returns:
            object: tenant.
        """
        tenant = self._client.create(name=tenant_name, domain=domain)

        if check:
            self.check_tenant_presence(tenant)
            assert_that(tenant.name, equal_to(tenant_name))
            if hasattr(domain, 'id'):
                domain_id = domain.id
            else:
                domain_id = domain
            assert_that(tenant.domain_id, equal_to(domain_id))

        return tenant

    @steps_checker.step
    def delete_tenant(self, tenant, check=True):
        """Step to delete tenant.

        Args:
            tenant (object): keystone tenant.
            check (bool): flag whether to check step or not.

        Raises:
            TimeoutExpired: if check failed after timeout.
        """
        self._client.delete(tenant.id)

        if check:
            self.check_tenant_presence(tenant, must_present=False)

    @steps_checker.step
    def check_tenant_presence(self, tenant, must_present=True, timeout=0):
        """Check step that tenant is present.

        Args:
            tenant (object): keystone tenant to check presence status.
            must_present (bool): flag whether tenant should present or not.
            timeout (int): seconds to wait a result of check.

        Raises:
            TimeoutExpired: if check failed after timeout.
        """
        def _check_tenant_presence():
            try:
                self._client.get(tenant.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_tenant_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_tenants(self, check=True):
        """Step to get tenants.

        Args:
            check (bool): flag whether to check step or not.

        Returns:
            tenants (list): list of tenants.

        Raises:
            AssertionError: if no tenants found.
        """
        tenants = list(self._client.list())
        if check:
            assert_that(tenants, is_not(empty()))

        return tenants

    @steps_checker.step
    def get_current_tenant(self, session, check=True):
        """Step to get current tenant.

        Args:
            session (object): session object.
            check (bool): flag whether to check step or not.

        Raises:
            AssertionError: if id of retrieved tenant is not equal to
            session tenant id.

        Returns:
            object: tenant.
        """
        tenant_id = session.get_tenant_id()
        tenant = self._client.get(tenant_id)
        if check:
            assert_that(tenant.id, equal_to(tenant_id))
        return tenant

    @steps_checker.step
    def check_get_tenants_requires_authentication(self):
        """Step to check unauthorized request returns (HTTP 401)

        Raises:
            AssertionError: if check failed.
        """
        exception_message = "The request you have made requires authentication"
        assert_that(calling(self.get_tenants),
                    raises(exceptions.Unauthorized), exception_message)