"""
Glance fixtures.

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

from glanceclient.v2.client import Client
import pytest

from stepler import config
from stepler.glance.steps import GlanceSteps
from stepler.third_party.utils import generate_ids, get_file_path  # noqa

__all__ = [
    'create_image',
    'create_images',
    'glance_client',
    'glance_steps',
    'ubuntu_image',
    'cirros_image'
]


@pytest.fixture
def glance_client(session):
    """Function fixture to get glance client.

    Args:
        session (object): authenticated keystone session

    Returns:
        glanceclient.v2.client.Client: instantiated glance client
    """
    return Client(session=session)


@pytest.fixture
def glance_steps(glance_client):
    """Function fixture to get glance steps.

    Args:
        glance_client (object): instantiated glance client

    Returns:
        stepler.glance.steps.GlanceSteps: instantiated glance steps
    """
    return GlanceSteps(glance_client)


@pytest.yield_fixture
def create_images(glance_steps):
    """Function fixture to create images with options.

    Can be called several times during a test.
    After the test it destroys all created images.

    Args:
        glance_steps (object): instantiated glance steps

    Returns:
        function: function to create images as batch with options
    """
    images = []

    def _create_images(image_names, *args, **kwgs):
        _images = glance_steps.create_images(image_names, *args, **kwgs)
        images.extend(_images)
        return _images

    yield _create_images

    if images:
        glance_steps.delete_images(images)


@pytest.fixture
def create_image(create_images):
    """Function fixture to create single image with options.

    Can be called several times during a test.
    After the test it destroys all created images.

    Args:
        create_images (function): function to create images with options

    Returns:
        function: function to create single image with options
    """
    def _create_image(image_name, *args, **kwgs):
        return create_images([image_name], *args, **kwgs)[0]

    return _create_image


@pytest.fixture
def ubuntu_image(create_image):
    """Fixture to create ubuntu image with default options before test.

    Args:
        create_image (function): function to create image with options

    Returns:
        object: ubuntu glance image
    """
    image_name = next(generate_ids('ubuntu'))
    image_path = get_file_path(config.UBUNTU_QCOW2_URL)
    return create_image(image_name, image_path)


@pytest.fixture
def cirros_image(glance_steps):
    """Fixture to find cirros default image with default options before
    test.

    Args:
        glance_steps (object): instantiated glance steps

    Returns:
        object: cirros glance image
    """
    return glance_steps.find_image(name='TestVM')
