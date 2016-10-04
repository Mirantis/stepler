"""
Flavor fixtures.

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

from stepler.nova.steps import FlavorSteps
from stepler.third_party.utils import generate_ids

__all__ = [
    'create_flavor',
    'flavor',
    'flavor_steps',
    'tiny_flavor'
]


@pytest.fixture
def flavor_steps(nova_client):
    """Fixture to get flavor steps."""
    return FlavorSteps(nova_client.flavors)


@pytest.yield_fixture
def create_flavor(flavor_steps):
    """Fixture to create flavor with options.

    Can be called several times during test.
    """
    flavors = []

    def _create_flavor(flavor_name):
        flavor = flavor_steps.create_flavor(flavor_name)
        flavors.append(flavor)
        return flavor

    yield _create_flavor

    for flavor in flavors:
        flavor_steps.delete_flavor(flavor)


@pytest.fixture
def flavor(create_flavor):
    """Fixture to create flavor with default options before test."""
    flavor_name = next(generate_ids('flavor'))
    return create_flavor(flavor_name)


@pytest.fixture
def tiny_flavor(flavor_steps):
    """
    Function fixture to find tiny flavor before test.

    Args:
        flavor_steps (object): instantiated flavor steps

    Returns:
        object: tiny flavor
    """
    return flavor_steps.get_flavor(name='m1.tiny')
