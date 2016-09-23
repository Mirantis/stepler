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

from stepler.glance.steps import GlanceSteps
from stepler import config
from stepler.utils import generate_ids, get_file_path

__all__ = [
    'create_image',
    'create_images',
    'glance_client',
    'glance_steps',
    'ubuntu_image'
]


@pytest.fixture
def glance_client(session):
    """Fixture to get glance client."""
    return Client(session=session)


@pytest.fixture
def glance_steps(glance_client):
    """Fixture to get glance steps."""
    return GlanceSteps(glance_client)


@pytest.yield_fixture
def create_images(glance_steps):
    """Fixture to create images with options.

    Can be called several times during test.
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
    """Fixture to create image with options.

    Can be called several times during test.
    """
    def _create_image(image_name, *args, **kwgs):
        return create_images([image_name], *args, **kwgs)[0]

    return _create_image


@pytest.fixture
def ubuntu_image(create_image):
    """Fixture to create image with default options before test."""
    image_name = next(generate_ids('ubuntu'))
    image_path = get_file_path(config.UBUNTU_QCOW2_URL)
    return create_image(image_name, image_path)
