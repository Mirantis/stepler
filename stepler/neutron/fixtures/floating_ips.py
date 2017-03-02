"""
--------------------
Floating ip fixtures
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

import pytest

from stepler.neutron import steps

__all__ = [
    'create_floating_ip',
    'floating_ip',
    'floating_ip_steps',
    'get_floating_ip_steps',
]


@pytest.fixture(scope="session")
def get_floating_ip_steps(get_neutron_client):
    """Callable session fixture to get router steps.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client

    Returns:
        function: function to get instantiated floating_ip steps
    """

    def _get_steps(**credentials):
        return steps.FloatingIPSteps(
            get_neutron_client(**credentials).floating_ips)

    return _get_steps


@pytest.fixture
def floating_ip_steps(get_floating_ip_steps):
    """Function fixture to get floating_ip steps.

    Args:
        get_floating_ip_steps (function): function to get instantiated
            floating_ip steps

    Returns:
        stepler.neutron.steps.SubnetSteps: instantiated floating_ip steps
    """
    return get_floating_ip_steps()


@pytest.fixture
def create_floating_ip(floating_ip_steps, public_network):
    """Fixture to create floating_ip with options.

    Can be called several times during a test.
    After the test it destroys all created floating_ips.

    Args:
        floating_ip_steps (object): instantiated floating ip steps
        public_network (obj): public network

    Returns:
        function: function to create floating_ip as batch with options
    """
    floating_ips = []

    def _create_floating_ip(network=None, **kwargs):
        network = network or public_network
        floating_ip = floating_ip_steps.create(network=network, **kwargs)
        floating_ips.append(floating_ip)
        return floating_ip

    yield _create_floating_ip

    for floating_ip in floating_ips:
        floating_ip_steps.delete(floating_ip)


@pytest.fixture
def floating_ip(create_floating_ip):
    """Fixture to create floating_ip with default options before test.

    Args:
        create_floating_ip (function): function to create floating_ip with
            options

    Returns:
        dict: floating_ip
    """
    return create_floating_ip()
