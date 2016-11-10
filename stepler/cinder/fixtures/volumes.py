"""
---------------
Volume fixtures
---------------
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

import logging

import pytest

from stepler.cinder import steps
from stepler import config

__all__ = [
    'get_volume_steps',
    'volume_steps',
    'upload_volume_to_image',
    'volume',
    'volumes_cleanup',
]

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def volumes_cleanup(volume_steps):
    """Function fixture to clear created volumes after test.

    It stores ids of all volumes before test and removes all new
    volumes after test.

    Args:
        volume_steps (object): instantiated volume steps
    """
    preserve_volume_ids = set(
        volume.id for volume in volume_steps.get_volumes(check=False))

    yield

    deleting_volumes = []
    for volume in volume_steps.get_volumes(check=False):
        if volume.id not in preserve_volume_ids:
            deleting_volumes.append(volume)

    volume_steps.delete_volumes(deleting_volumes)


@pytest.fixture(scope='session')
def get_volume_steps(get_cinder_client):
    """Callable session fixture to get volume steps.

    Args:
        get_cinder_client (function): function to get cinder client

    Returns:
        function: function to get volume steps
    """
    def _get_volume_steps(**credentials):
        return steps.VolumeSteps(get_cinder_client(**credentials))

    return _get_volume_steps


@pytest.fixture
def volume_steps(get_volume_steps, uncleanable):
    """Function fixture to get volume steps.

    Args:
        get_volume_steps (function): function to get volume steps
        uncleanable (AttrDict): data structure with skipped resources

    Yields:
        stepler.cinder.steps.VolumeSteps: instantiated volume steps
    """
    def _get_volumes():
        # check=False because in best case no volumes will be
        return _volume_steps.get_volumes(
            metadata={config.STEPLER_PREFIX: config.STEPLER_PREFIX},
            check=False)

    _volume_steps = get_volume_steps()
    volume_ids_before = [volume.id for volume in _get_volumes()]

    yield _volume_steps

    deleting_volumes = []
    for volume in _get_volumes():
        if volume.id not in uncleanable.volume_ids:
            if volume.id not in volume_ids_before:
                deleting_volumes.append(volume)

    _volume_steps.delete_volumes(deleting_volumes)


@pytest.yield_fixture
def upload_volume_to_image(volume_steps, glance_steps):
    """Callable function fixture to upload volume to image.

    Can be called several times during a test.
    After the test it destroys all created objects.

    Args:
        volume_steps (VolumeSteps): instantiated volume steps
        glance_steps (GlanceSteps): instantiated glance steps

    Returns:
        function: function to upload volume to image
    """
    images = []

    def _upload_volume_to_image(disk_format):
        volume = volume_steps.create_volumes()[0]
        image_info = volume_steps.volume_upload_to_image(
            volume=volume, disk_format=disk_format)

        image = glance_steps.get_image(
            id=image_info['os-volume_upload_image']['image_id'])
        images.append(image)
        glance_steps.check_image_status(image, status='active',
                                        timeout=config.IMAGE_AVAILABLE_TIMEOUT)
        return image

    yield _upload_volume_to_image

    if images:
        glance_steps.delete_images(images)


@pytest.fixture
def volume(volume_steps):
    """Function fixture to create volume with default options before test.

    Args:
        volume_steps (VolumeSteps): instantiated volume steps

    Returns:
        object: cinder volume
    """
    return volume_steps.create_volumes()[0]
