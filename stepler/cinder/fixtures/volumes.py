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

import pytest

from stepler.cinder import steps
from stepler import config

__all__ = [
    'cleanup_volumes',
    'get_volume_steps',
    'primary_volumes',
    'unexpected_volumes_cleanup',
    'upload_volume_to_image',
    'volume',
    'volume_steps',
]


@pytest.fixture(scope='session')
@pytest.mark.usefixtures('big_volume_quota')
def get_volume_steps(get_cinder_client):
    """Callable session fixture to get volume steps.

    Args:
        get_cinder_client (function): function to get cinder client

    Returns:
        function: function to get volume steps
    """
    def _get_volume_steps(version, is_api, **credentials):
        return steps.VolumeSteps(
            get_cinder_client(version, is_api, **credentials).volumes)

    return _get_volume_steps


@pytest.fixture
def unexpected_volumes_cleanup(primary_volumes,
                               get_volume_steps,
                               cleanup_volumes):
    """Function fixture to clear unexpected volumes.

    It provides cleanup before and after test.
    """
    if config.CLEANUP_UNEXPECTED_BEFORE_TEST:
        cleanup_volumes(get_volume_steps(config.CURRENT_CINDER_VERSION,
                                         is_api=False),
                        config.UNEXPECTED_VOLUMES_LIMIT)

    yield

    if config.CLEANUP_UNEXPECTED_AFTER_TEST:
        cleanup_volumes(get_volume_steps(config.CURRENT_CINDER_VERSION,
                                         is_api=False),
                        config.UNEXPECTED_VOLUMES_LIMIT)


@pytest.fixture
def volume_steps(unexpected_volumes_cleanup,
                 get_volume_steps,
                 cleanup_volumes):
    """Function fixture to get volume steps.

    Args:
        get_volume_steps (function): function to get volume steps
        cleanup_volumes (function): function to cleanup volumes after test

    Yields:
        VolumeSteps: instantiated volume steps
    """
    _volume_steps = get_volume_steps(
        config.CURRENT_CINDER_VERSION, is_api=False)
    volumes = _volume_steps.get_volumes(check=False)
    volume_ids_before = {volume.id for volume in volumes}

    yield _volume_steps
    cleanup_volumes(_volume_steps, uncleanable_ids=volume_ids_before)


@pytest.fixture(scope='session')
def primary_volumes(get_volume_steps,
                    cleanup_volumes,
                    uncleanable):
    """Session fixture to remember primary volumes before tests.

    Also optionally in finalization it deletes all unexpected volumes which
    are remained after tests.

    Args:
        get_volume_steps (function): Function to get volume steps.
        cleanup_volumes (function): Function to cleanup volumes.
        uncleanable (AttrDict): Data structure with skipped resources.
    """
    volume_ids_before = set()
    for volume in get_volume_steps(
            config.CURRENT_CINDER_VERSION, is_api=False).get_volumes(
                check=False):
        uncleanable.volume_ids.add(volume.id)
        volume_ids_before.add(volume.id)

    yield

    if config.CLEANUP_UNEXPECTED_AFTER_ALL:
        cleanup_volumes(
            get_volume_steps(
                config.CURRENT_CINDER_VERSION, is_api=False),
            uncleanable_ids=volume_ids_before)


@pytest.fixture(scope='session')
def cleanup_volumes(uncleanable):
    """Callable session fixture to cleanup volumes.

    Args:
        uncleanable (AttrDict): Data structure with resources to skip cleanup.
    """
    def _cleanup_volumes(_volume_steps, limit=0, uncleanable_ids=None):
        uncleanable_ids = uncleanable_ids or uncleanable.volume_ids
        deleting_volumes = []

        for volume in _volume_steps.get_volumes(check=False):
            if (volume.id not in uncleanable_ids and
                    volume.status != config.STATUS_DELETING):
                deleting_volumes.append(volume)

        if len(deleting_volumes) > limit:
            _volume_steps.delete_volumes(deleting_volumes, cascade=True)

    return _cleanup_volumes


@pytest.fixture
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
    def _upload_volume_to_image(disk_format):
        volume = volume_steps.create_volumes()[0]
        image_info = volume_steps.volume_upload_to_image(
            volume=volume, disk_format=disk_format)

        image = glance_steps.get_image(
            id=image_info['os-volume_upload_image']['image_id'])
        glance_steps.check_image_status(image, status='active',
                                        timeout=config.IMAGE_AVAILABLE_TIMEOUT)
        return image

    yield _upload_volume_to_image


@pytest.fixture
def volume(volume_steps):
    """Function fixture to create volume with default options before test.

    Args:
        volume_steps (VolumeSteps): instantiated volume steps

    Returns:
        object: cinder volume
    """
    return volume_steps.create_volumes()[0]
