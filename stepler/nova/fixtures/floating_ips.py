"""
Floating IP fixtures.

@author: schipiga@mirantis.com
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

from stepler.nova.steps import FloatingIpSteps

__all__ = [
    'nova_create_floating_ip',
    'nova_floating_ip',
    'nova_floating_ip_steps'
]


@pytest.fixture
def nova_floating_ip_steps(nova_client):
    """Fixture to get floating_ip steps."""
    return FloatingIpSteps(nova_client)


@pytest.yield_fixture
def nova_create_floating_ip(nova_floating_ip_steps):
    """Fixture to create floating_ip with options.

    Can be called several times during test.
    """
    floating_ips = []

    def _create_floating_ip():
        floating_ip = nova_floating_ip_steps.create_floating_ip()
        floating_ips.append(floating_ip)
        return floating_ip

    yield _create_floating_ip

    for floating_ip in floating_ips:
        nova_floating_ip_steps.delete_floating_ip(floating_ip)


@pytest.fixture
def nova_floating_ip(nova_create_floating_ip):
    """Fixture to create floating_ip with default options before test."""
    return nova_create_floating_ip()
