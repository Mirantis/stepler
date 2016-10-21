"""
-------------
Zone fixtures
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

import pytest

from stepler.nova import steps

__all__ = [
    'zone_steps',
    'nova_zone',
    'nova_zone_hosts'
]

# TODO(akoryagin) Merge with 'availability_zones.py'


@pytest.fixture
def zone_steps(nova_client):
    """Fixture to get zone steps.

    Args:
        nova_client (function): nova client

    Returns:
        ZoneSteps: instantiated zone steps.
    """
    return steps.ZoneSteps(nova_client.availability_zones)


@pytest.fixture
def nova_zone(zone_steps):
    """Fixture to get one available nova zone object.

    Args:
        zone_steps (function): zone steps

    Returns:
        object: nova zone object.
    """
    return zone_steps.get_zone(**{'zoneName': 'nova',
                                  'zoneState': {'available': True}})


@pytest.fixture
def nova_zone_hosts(nova_zone):
    """Fixture to get all hosts from nova zone.

    Args:
        nova_zone (object): nova zone object.

    Returns:
        list: str FQDN values
    """
    return nova_zone.hosts.keys()
