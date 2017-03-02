"""
--------------------
Floating IP fixtures
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

import warnings

import attrdict
import pytest

from stepler.nova.steps import FloatingIpSteps

__all__ = [
    'get_nova_floating_ip_steps',
    'nova_floating_ip',
    'nova_floating_ip_steps',
]


@pytest.fixture(scope="session")
def get_nova_floating_ip_steps(get_nova_client):
    """Callable session fixture to get nova floating ip steps.

    Args:
        get_nova_client (function): function to get instantiated nova client

    Returns:
        function: function to get instantiated nova floating_ip steps
    """

    warnings.warn("Nova API from 2.36 microversion is not supported floating "
                  "ip creation. Use `get_floating_ip_steps` instead",
                  DeprecationWarning)

    def _get_steps(**credentials):
        return FloatingIpSteps(get_nova_client(**credentials))

    return _get_steps


@pytest.fixture
def nova_floating_ip_steps(get_nova_floating_ip_steps):
    """Fixture to get floating_ip steps."""

    warnings.warn("Nova API from 2.36 microversion is not supported floating "
                  "ip creation. Use `floating_ip_steps` instead",
                  DeprecationWarning)

    return get_nova_floating_ip_steps()


@pytest.fixture
def nova_floating_ip(floating_ip):
    """Fixture to create floating_ip with default options before test."""

    warnings.warn("Nova API from 2.36 microversion is not supported floating "
                  "ip creation. Use `floating_ip` instead", DeprecationWarning)

    floating_ip = floating_ip.copy()
    floating_ip['ip'] = floating_ip['floating_ip_address']
    return attrdict.AttrDict(floating_ip)
