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

from hamcrest import assert_that, is_not  # noqa
import pytest

from stepler.cinder import steps
from stepler import config
from stepler.third_party import utils

__all__ = [
    'create_volume',
    'create_volumes',
    'volume',
    'volume_steps',
    'upload_volume_to_image',
    'volume',
    'volumes_cleanup',
]

LOGGER = logging.getLogger(__name__)
# volumes which should be missed, when unexpected volumes will be removed
SKIPPED_VOLUMES = []


@pytest.yield_fixture
def volumes_cleanup():
    """Callable function fixture to clear unexpected volumes.

    It provides cleanup before and after test.
    Cleanup before test is callable with injection of volume steps.
    Should be called before returning of instantiated volume steps.
    """
    _volume_steps = [None]

    def _volumes_cleanup(volume_steps):
        assert_that(volume_steps, is_not(None))
        _volume_steps[0] = volume_steps  # inject volume steps for finalizer
        # check=False because in best case no volumes will be present
        volumes = volume_steps.get_volumes(name_prefix=config.STEPLER_PREFIX,
                                           check=False)
        if SKIPPED_VOLUMES:
            volume_names = [volume.name for volume in SKIPPED_VOLUMES]

            LOGGER.debug(
                "SKIPPED_VOLUMES contains volumes {!r}. They will not be "
                "removed in cleanup procedure.".format(volume_names))

            volumes = [volume for volume in volumes
                       if volume not in SKIPPED_VOLUMES]
        if volumes:
            volume_steps.delete_volumes(volumes)

    yield _volumes_cleanup

    _volumes_cleanup(_volume_steps[0])


@pytest.fixture
def volume_steps(cinder_client, volumes_cleanup):
    """Function fixture to get volume steps.

    Args:
        cinder_client (object): instantiated cinder client
        volumes_cleanup (function): function to make volumes cleanup right
            after volume steps initialization

    Returns:
        stepler.cinder.steps.VolumeSteps: instantiated volume steps
    """
    _volume_steps = steps.VolumeSteps(cinder_client)
    volumes_cleanup(_volume_steps)
    return _volume_steps


@pytest.yield_fixture
def create_volumes(volume_steps, server_steps, detach_volume_from_server):
    """Callable function fixture to create volumes with options.

    Can be called several times during a test.
    After the test it destroys all created volumes.

    Args:
        volume_steps (object): instantiated volume steps

    Returns:
        function: function to create volumes as batch with options
    """
    volumes = []

    def _create_volumes(names, *args, **kwgs):
        _volumes = volume_steps.create_volumes(names, *args, **kwgs)
        volumes.extend(_volumes)
        return _volumes

    yield _create_volumes

    if volumes:
        for volume in volumes:
            attached_server_ids = volume_steps.get_servers_attached_to_volume(
                volume)
            for server_id in attached_server_ids:
                server = server_steps.get_server(id=server_id)
                detach_volume_from_server(volume, server)
        volume_steps.delete_volumes(volumes)


@pytest.fixture
def create_volume(create_volumes):
    """Callable function fixture to create single volume with options.

    Can be called several times during a test.
    After the test it destroys all created volumes.

    Args:
        create_volumes (function): function to create volumes with options

    Returns:
        function: function to create single volume with options
    """
    def _create_volume(name=None, *args, **kwgs):
        return create_volumes([name], *args, **kwgs)[0]

    return _create_volume


@pytest.yield_fixture
def upload_volume_to_image(create_volume, volume_steps, glance_steps):
    """Callable function fixture to upload volume to image.

    Can be called several times during a test.
    After the test it destroys all created objects.

    Args:
        create_volume (function): function to create volume with options
        volume_steps (VolumeSteps): instantiated volume steps
        glance_steps (GlanceSteps): instantiated glance steps

    Returns:
        function: function to upload volume to image
    """
    images = []

    def _upload_volume_to_image(volume_name, image_name, disk_format):
        volume = create_volume(volume_name)
        image_info = volume_steps.volume_upload_to_image(
            volume=volume, image_name=image_name, disk_format=disk_format)
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
def volume(create_volume):
    """Function fixture to create volume with default options before test.

    Args:
        create_volume (function): function to create single volume with options

    Returns:
        object: cinder volume
    """
    volume_name = next(utils.generate_ids('volume'))
    return create_volume(name=volume_name)
