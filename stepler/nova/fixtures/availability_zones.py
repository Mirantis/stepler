"""
--------------------------
Availability zone fixtures
--------------------------
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

from stepler.nova import steps

__all__ = [
    'get_availability_zone_steps',
    'availability_zone_steps',
    'nova_availability_zone',
    'nova_availability_zone_hosts'
]


@pytest.fixture(scope='session')
def get_availability_zone_steps(get_nova_client):
    """Callable session fixture to get availability zone steps.

    Args:
        get_nova_client (function): function to get nova client.

    Returns:
        function: function to get availability zone steps.
    """

    def _get_availability_zone_steps():
        client = get_nova_client()
        return steps.AvailabilityZoneSteps(client.availability_zones)
    return _get_availability_zone_steps


@pytest.fixture
def availability_zone_steps(get_availability_zone_steps):
    """Fixture to get availability zone steps.

    Args:
        get_availability_zone_steps (function): function to get availability
                                                zone steps.

    Returns:
        ZoneSteps: instantiated zone steps.
    """
    return get_availability_zone_steps()


@pytest.fixture
def nova_availability_zone(availability_zone_steps):
    """Fixture to get one available nova zone object.

    Args:
        availability_zone_steps (function): zone steps

    Returns:
        object: nova zone object.
    """
    return availability_zone_steps.get_zone(
        **{'zoneName': 'nova',
           'zoneState': {'available': True}})


@pytest.fixture
def nova_availability_zone_hosts(nova_availability_zone):
    """Fixture to get all hosts from nova zone.

    Args:
        nova_availability_zone (object): nova zone object.

    Returns:
        list: str FQDN values
    """
    return nova_availability_zone.hosts.keys()
