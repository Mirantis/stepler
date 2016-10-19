"""
---------------
Glance fixtures
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

from glanceclient.v2.client import Client
import pytest

from stepler import config
from stepler.glance.steps import GlanceSteps
from stepler.third_party.utils import generate_ids, get_file_path  # noqa

__all__ = [
    'create_image',
    'create_images',
    'get_glance_client',
    'get_glance_steps',
    'glance_client',
    'glance_steps',
    'ubuntu_image',
    'cirros_image',
    'ubuntu_qcow2_image_for_cinder',
    'ubuntu_raw_image_for_cinder'
]

LOGGER = logging.getLogger(__name__)
# images which should be missed, when unexpected images will be removed
SKIPPED_IMAGES = []  # TODO(schipiga): describe its mechanism in docs


def _remove_stayed_images(glance_steps):
    """Clear unexpected images.

    We should remove images which unexpectedly stayed after tests.

    Args:
        glance_steps (GlanceSteps): instantiated glance steps
    """
    # check=False because in best case no stayed images will be present
    images = glance_steps.get_images(name_prefix=config.STEPLER_PREFIX,
                                     check=False)
    if SKIPPED_IMAGES:
        image_names = [image.name for image in SKIPPED_IMAGES]
        LOGGER.warn("SKIPPED_IMAGES contains images {!r}. "
                    "They will not be removed.".format(image_names))

    images = [image for image in images if image not in SKIPPED_IMAGES]
    glance_steps.delete_images(images)


@pytest.fixture(scope='session')
def get_glance_client(get_session):
    """Callable session fixture to get glance client.

    Args:
        get_session (function): function to get keystone session

    Returns:
        function: function to get glance client
    """
    def _get_glance_client():
        return Client(session=get_session())

    return _get_glance_client


@pytest.fixture
def glance_client(get_glance_client):
    """Function fixture to get glance client.

    Args:
        get_glance_client (function): function to get glance client

    Returns:
        glanceclient.v2.client.Client: instantiated glance client
    """
    return get_glance_client()


@pytest.fixture(scope='session')
def get_glance_steps(get_glance_client):
    """Callable session fixture to get glance steps.

    Args:
        get_glance_client (function): function to get glance client

    Returns:
        function: function to get glance steps
    """
    def _get_glance_steps():
        glance_steps = GlanceSteps(get_glance_client())
        _remove_stayed_images(glance_steps)  # remove when steps are requested
        return glance_steps

    return _get_glance_steps


@pytest.fixture
def glance_steps(get_glance_steps):
    """Function fixture to get glance steps.

    Args:
        get_glance_steps (function): function to get glance steps

    Returns:
        GlanceSteps: instantiated glance steps
    """
    return get_glance_steps()


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


@pytest.yield_fixture(scope='session')
def ubuntu_image(get_glance_steps):
    """Session fixture to create ubuntu image with default options.

    Args:
        get_glance_steps (function): function to get glance steps

    Returns:
        object: ubuntu glance image
    """
    image_name = next(generate_ids('ubuntu'))
    image_path = get_file_path(config.UBUNTU_QCOW2_URL)

    _ubuntu_image = get_glance_steps().create_images([image_name],
                                                     image_path)[0]
    SKIPPED_IMAGES.append(_ubuntu_image)

    yield _ubuntu_image

    get_glance_steps().delete_images([_ubuntu_image])
    SKIPPED_IMAGES.remove(_ubuntu_image)


@pytest.yield_fixture(scope='session')
def cirros_image(get_glance_steps):
    """Session fixture to create cirros image with default options.

    Args:
        get_glance_steps (function): function to get glance steps

    Returns:
        object: cirros glance image
    """
    image_name = next(generate_ids('cirros'))
    image_path = get_file_path(config.CIRROS_QCOW2_URL)

    _cirros_image = get_glance_steps().create_images([image_name],
                                                     image_path)[0]
    SKIPPED_IMAGES.append(_cirros_image)

    yield _cirros_image

    get_glance_steps().delete_images([_cirros_image])
    SKIPPED_IMAGES.remove(_cirros_image)


@pytest.yield_fixture(scope='session')
def ubuntu_qcow2_image_for_cinder(get_glance_steps):
    """Session fixture to create ubuntu image with default options.
    Args:
        get_glance_steps (function): function to get glance steps
    Returns:
        object: ubuntu glance image
    """
    image_name = next(generate_ids('ubuntu'))
    image_path = get_file_path(config.UBUNTU_ISO_URL)

    _ubuntu_image = get_glance_steps().create_images([image_name],
                                                     image_path, )[0]
    SKIPPED_IMAGES.append(_ubuntu_image)

    yield _ubuntu_image

    get_glance_steps().delete_images([_ubuntu_image])
    SKIPPED_IMAGES.remove(_ubuntu_image)


@pytest.yield_fixture(scope='session')
def ubuntu_raw_image_for_cinder(get_glance_steps):
    """Session fixture to create ubuntu image with default options.
    Args:
        get_glance_steps (function): function to get glance steps
    Returns:
        object: ubuntu glance image
    """
    image_name = next(generate_ids('ubuntu'))
    image_path = get_file_path(config.UBUNTU_ISO_URL)

    _ubuntu_image = get_glance_steps().create_images([image_name],
                                                     image_path,
                                                     disk_format='raw')[0]
    SKIPPED_IMAGES.append(_ubuntu_image)

    yield _ubuntu_image

    get_glance_steps().delete_images([_ubuntu_image])
    SKIPPED_IMAGES.remove(_ubuntu_image)
