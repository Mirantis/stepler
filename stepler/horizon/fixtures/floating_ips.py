"""
-------------------------
Fixtures for floating IPs
-------------------------
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

from stepler.horizon import steps
from stepler.third_party import utils

__all__ = [
    'allocate_floating_ip',
    'floating_ip',
    'floating_ips_steps_ui',
]


@pytest.fixture
def floating_ips_steps_ui(network_setup, login, horizon):
    """Fixture to get floating IPs steps.

    Args:
        network_setup (None): should set up network before steps using
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.FloatingIPsSteps: instantiated floating IP steps
    """
    return steps.FloatingIPsSteps(horizon)


@pytest.fixture
def allocate_floating_ip(floating_ips_steps_ui):
    """Fixture to create floating IP with options.

    Can be called several times during test.

    Args:
        floating_ips_steps_ui (object): instantiated floating ips steps

    Yields:
        function: function to allocate floating IP
    """
    floating_ips = []

    def _allocate_floating_ip():
        ip = floating_ips_steps_ui.allocate_floating_ip()
        floating_ip = utils.AttrDict(ip=ip)
        floating_ips.append(floating_ip)
        return floating_ip

    yield _allocate_floating_ip

    for floating_ip in floating_ips:
        floating_ips_steps_ui.release_floating_ip(floating_ip.ip)


@pytest.fixture
def floating_ip(allocate_floating_ip):
    """Fixture to create floating IP with default options before test.

    Args:
        allocate_floating_ip (function): function to allocate floating IP

    Returns:
        AttrDict: floating IP
    """
    return allocate_floating_ip()
