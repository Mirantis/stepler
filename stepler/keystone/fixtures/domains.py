"""
Domain fixtures.

@author: mshalamov@mirantis.com
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

from stepler.keystone.steps import DomainSteps
from stepler.utils import generate_ids

__all__ = [
    'create_domain',
    'domain_steps',
    'domain'
]


@pytest.fixture
def domain_steps(keystone_client):
    """Fixture to get domain steps."""
    return DomainSteps(keystone_client.domains)


@pytest.yield_fixture
def create_domain(domain_steps):
    """Fixture to create domain with options.

    Can be called several times during test.
    """
    domains = []

    def _create_domain(domain_name):
        domain = domain_steps.create_domain(domain_name)
        domains.append(domain)
        return domain

    yield _create_domain

    for domain in domains:
        domain_steps.delete_domain(domain)


@pytest.fixture
def domain(create_domain):
    """Fixture to create domain with default options before test."""
    domain_name = next(generate_ids('domain'))
    return create_domain(domain_name)
