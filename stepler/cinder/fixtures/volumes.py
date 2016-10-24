"""
---------------
Cinder fixtures
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
    'create_volume',
    'create_volumes',
    'volume_steps',
    'upload_volume_to_image',
]


@pytest.fixture
def volume_steps(cinder_client):
    """Function fixture to get volume steps.

    Args:
        cinder_client (object): instantiated cinder client

    Returns:
        stepler.cinder.steps.VolumeSteps: instantiated volume steps
    """
    return steps.VolumeSteps(cinder_client)


@pytest.yield_fixture
def create_volumes(volume_steps):
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
        volume_steps.detach_volumes(volumes)
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
            image_info['os-volume_upload_image']['image_id'])
        images.append(image)
        glance_steps.check_image_status(image, status='active',
                                        timeout=config.IMAGE_AVAILABLE_TIMEOUT)
        return image

    yield _upload_volume_to_image

    if images:
        glance_steps.delete_images(images)
