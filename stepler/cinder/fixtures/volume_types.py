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

__all__ = [
    'volume_types_steps',
    'create_volume_type',
]


@pytest.fixture
def volume_types_steps(cinder_client):
    """Function fixture to get cinder volume types steps.

    Args:
        cinder_client (object): instantiated cinder client

    Returns:
        stepler.cinder.steps.CinderVolumeTypesSteps: instantiated types steps
    """
    return steps.VolumeTypesSteps(cinder_client.volume_types)


@pytest.yield_fixture
def create_volume_type(volume_types_steps):
    """Callable fixture to create volume types with options.

    Can be called several times during test.
    """
    volume_types = []

    def _create_volume_type(name, description=None, is_public=True):
        volume_type = volume_types_steps.create_volume_type(
            name=name, description=description, is_public=is_public)
        volume_types.append(volume_type)
        return volume_type

    yield _create_volume_type

    for volume_type in volume_types:
        volume_types_steps.delete_volume_type(volume_type)
