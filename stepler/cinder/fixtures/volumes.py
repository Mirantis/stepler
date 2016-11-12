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

from hamcrest import assert_that, is_not  # noqa
import pytest

from stepler.cinder import steps
from stepler import config

__all__ = [
    'get_volume_steps',
    'primary_volumes',
    'volume',
    'volume_steps',
    'volumes_cleanup',
    'unexpected_volumes_cleanup',
    'upload_volume_to_image',
]


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
def unexpected_volumes_cleanup(get_volume_steps,
                               cleanup_volumes):
    """Callable function fixture to clear unexpected volumes.

    It provides cleanup before and after test.
    """
    if config.CLEANUP_UNEXPECTED_BEFORE:
        _cleanup_volumes(get_volume_steps(), config.UNEXPECTED_VOLUMES_LIMIT)

    yield

    if config.CLEANUP_UNEXPECTED_AFTER:
        _cleanup_volumes(get_volume_steps(), config.UNEXPECTED_VOLUMES_LIMIT)


@pytest.fixture
def volume_steps(unexpected_volumes_cleanup,
                 get_volume_steps,
                 cleanup_volumes):
    """Function fixture to get volume steps.

    Args:
        get_volume_steps (function): function to get volume steps
        volumes_cleanup (function): function to cleanup volumes after test

    Yields:
        VolumeSteps: instantiated volume steps
    """
    _volume_steps = get_volume_steps()
    volumes = _volume_steps.get_volumes(all_projects=True, check=False)
    volume_ids_before = {volume.id for volume in volumes}

    yield _volume_steps
    cleanup_volumes(_volume_steps, uncleanable_ids=volume_ids_before)


@pytest.fixture(scope='session', autouse=True)
def primary_volumes(get_volume_steps,
                    cleanup_volumes,
                    uncleanable):
    """Session fixture to remember primary volumes before tests.

    Also in finalization it deletes all unexpected volumes which are remained
    after tests.

    Args:
        get_volume_steps (function): Function to get volume steps.
        cleanup_volumes (function): Function to cleanup volumes.
        uncleanable (AttrDict): Data structure with skipped resources.
    """
    volume_ids_ before = set()
    for volume in get_volume_steps().get_volumes(all_projects=True,
                                                 check=False):
        uncleanable.volume_ids.add(volume.id)
        volume_ids_before.add(volume.id)

    yield
    cleanup_volumes(get_volume_steps(), uncleanable_ids=volume_ids_before)


@pytest.fixture(scope='session')
def cleanup_volumes(uncleanable):
    """Session fixture to cleanup volumes.

    Args:
        uncleanable (AttrDict): Data structure with skipped resources.
    """
    def _cleanup_volumes(_volume_steps, limit=0, uncleanable_ids=None):
        uncleanable_ids = uncleanable_ids or uncleanable.volume_ids
        deleting_volumes = []

        for volume in _volume_steps.get_volumes(all_projects=True,
                                                check=False):
            if volume.id not in uncleanable_ids:
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
