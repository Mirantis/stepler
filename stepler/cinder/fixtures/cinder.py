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

from cinderclient import client as cinderclient
import pytest

from stepler.cinder import steps

__all__ = [
    'create_volume',
    'create_volumes',
    'cinder_client',
    'cinder_steps',
    'volume_upload_to_image',
]


@pytest.fixture
def cinder_client(session):
    """Function fixture to get cinder client.

    Args:
        session (object): authenticated keystone session

    Returns:
        cinderclient.client.Client: instantiated cinder client
    """
    return cinderclient.Client(version=2, session=session)


@pytest.fixture
def cinder_steps(cinder_client):
    """Function fixture to get cinder steps.

    Args:
        cinder_client (object): instantiated cinder client

    Returns:
        stepler.cinder.steps.GlanceSteps: instantiated cinder steps
    """
    return steps.CinderSteps(cinder_client)


@pytest.yield_fixture
def create_volumes(cinder_steps):
    """Function fixture to create volumes with options.

    Can be called several times during a test.
    After the test it destroys all created volumes.

    Args:
        cinder_steps (object): instantiated cinder steps

    Returns:
        function: function to create volumes as batch with options
    """
    volumes = []

    def _create_volumes(names, *args, **kwgs):
        _volumes = cinder_steps.create_volumes(names, *args, **kwgs)
        volumes.extend(_volumes)
        return _volumes

    yield _create_volumes

    if volumes:
        cinder_steps.delete_volumes(volumes)


@pytest.fixture
def create_volume(create_volumes):
    """Function fixture to create single volume with options.

    Can be called several times during a test.
    After the test it destroys all created volumes.

    Args:
        create_volumes (function): function to create volumes with options

    Returns:
        function: function to create single volume with options
    """
    def _create_volume(name, *args, **kwgs):
        return create_volumes([name], *args, **kwgs)[0]

    return _create_volume


@pytest.fixture
def volume_upload_to_image(cinder_steps):
    """Function fixture to upload volume to image with options.

    Can be called several times during a test.
    After the test it destroys all created images.

    Args:
        cinder_steps (object): instantiated cinder steps

    Returns:
        function: function to create single image with options
    """
    def _volume_upload_to_image(volume, image_name, force, container_format,
                                disk_format):
        return cinder_steps.volume_upload_to_image(volume, image_name,
                                                   force, container_format,
                                                   disk_format)

    return _volume_upload_to_image
