"""
----------------
Tenant fixtures
----------------
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

import pytest

from stepler.keystone import steps
from stepler.third_party.utils import generate_ids

__all__ = [
    'create_tenant',
    'get_tenant_steps',
    'tenant_steps',
    'tenant',
    'current_tenant',
]


@pytest.fixture(scope="session")
def get_tenant_steps(get_keystone_client):
    """Callable session fixture to get tenant steps.

    Args:
        get_keystone_client (function): function to get keystone client.

    Returns:
        function: function to get tenant steps.
    """
    def _get_steps(**credentials):
        import ipdb; ipdb.set_trace()
        return steps.TenantSteps(get_keystone_client(**credentials).tenants)

    return _get_steps


@pytest.fixture
def tenant_steps(get_tenant_steps):
    """Function fixture to get tenant steps.

    Args:
        get_tenant_steps (function): function to get tenant steps.

    Returns:
        tenantSteps: instantiated tenant steps.
    """
    return get_tenant_steps()


@pytest.yield_fixture
def create_tenant(tenant_steps):
    """Fixture to create tenant with options.

    Can be called several times during test.
    """
    tenants = []

    def _create_tenant(*args, **kwargs):
        tenant = tenant_steps.create_tenant(*args, **kwargs)
        tenants.append(tenant)
        return tenant

    yield _create_tenant

    for tenant in tenants:
        tenant_steps.delete_tenant(tenant)


@pytest.fixture
def tenant(create_tenant):
    """Fixture to create tenant with default options before test."""
    tenant_name = next(generate_ids('tenant'))
    return create_tenant(tenant_name)


@pytest.fixture
def current_tenant(session, tenant_steps):
    """Function fixture to get current tenant.

    Args:
        session (obj): instantiated keystone session.
        tenant_steps (obj): instantiated tenant steps.

    Returns:
        obj: current tenant.
    """
    return tenant_steps.get_current_tenant(session)
