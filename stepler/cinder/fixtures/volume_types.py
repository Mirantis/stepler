"""
----------------------------
Cinder volume types fixtures
----------------------------
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

from stepler.cinder import steps
from stepler.third_party import utils

__all__ = [
    'volume_type_steps',
    'create_volume_type',
    'volume_type',
]


@pytest.fixture
def volume_type_steps(cinder_client):
    """Function fixture to get cinder volume types steps.

    Args:
        cinder_client (object): instantiated cinder client

    Returns:
        stepler.cinder.steps.CinderVolumeTypeSteps: instantiated types steps
    """
    return steps.VolumeTypeSteps(cinder_client.volume_types)


@pytest.yield_fixture
def create_volume_type(volume_type_steps):
    """Callable fixture to create volume types with options.

    Can be called several times during test.

    Args:
        volume_type_steps (VolumeTypeSteps): instantiated volume type steps

    Yields:
        function: function to create singe volume type with options
    """
    volume_types = []

    def _create_volume_type(*args, **kwgs):
        volume_type = volume_type_steps.create_volume_type(*args, **kwgs)
        volume_types.append(volume_type)
        return volume_type

    yield _create_volume_type

    for volume_type in volume_types:
        volume_type_steps.delete_volume_type(volume_type)


@pytest.fixture
def volume_type(create_volume_type):
    """Fixture to create volume type with default options before test.

    Args:
        create_volume_type (function): function to create volume type

    Returns:
        object: volume type
    """

    volume_type_name = next(utils.generate_ids('volume_type'))
    return create_volume_type(volume_type_name)
