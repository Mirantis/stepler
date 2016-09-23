"""
Fixtures for floating IPs.

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

from stepler.horizon.steps import FloatingIPsSteps

from stepler.horizon.utils import AttrDict

__all__ = [
    'allocate_floating_ip',
    'floating_ip',
    'floating_ips_steps'
]


@pytest.fixture
def floating_ips_steps(login, horizon):
    """Fixture to get floating IPs steps."""
    return FloatingIPsSteps(horizon)


@pytest.yield_fixture
def allocate_floating_ip(floating_ips_steps):
    """Fixture to create floating IP with options.

    Can be called several times during test.
    """
    floating_ips = []

    def _allocate_floating_ip():
        ip = floating_ips_steps.allocate_floating_ip()
        floating_ip = AttrDict(ip=ip)
        floating_ips.append(floating_ip)
        return floating_ip

    yield _allocate_floating_ip

    for floating_ip in floating_ips:
        floating_ips_steps.release_floating_ip(floating_ip.ip)


@pytest.fixture
def floating_ip(allocate_floating_ip):
    """Fixture to create floating IP with default options before test."""
    return allocate_floating_ip()
