"""
-------------------
Fixtures for images
-------------------
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

from stepler import config
from stepler.glance.fixtures import create_images_context
from stepler.horizon.steps import ImagesSteps
from stepler.third_party import utils

__all__ = [
    'create_image',
    'create_images',
    'images',
    'image',
    'images_steps'
]


@pytest.fixture
def images_steps(login, horizon):
    """Fixture to get images steps."""
    return ImagesSteps(horizon)


@pytest.yield_fixture
def create_images(images_steps, horizon):
    """Fixture to create images with options.

    Can be called several times during test.
    """
    images = []

    def _create_images(*image_names):
        _images = []

        for image_name in image_names:
            images_steps.create_image(image_name, check=False)
            images_steps.close_notification('success')

            image = utils.AttrDict(name=image_name)
            images.append(image)
            _images.append(image)

        for image_name in image_names:
            horizon.page_images.table_images.row(
                name=image_name).wait_for_status('Active')

        return _images

    yield _create_images

    if images:
        images_steps.delete_images([image.name for image in images])


@pytest.yield_fixture
def create_image(images_steps):
    """Fixture to create image with options.

    Can be called several times during test.
    """
    images = []

    def _create_image(image_name, *args, **kwgs):
        images_steps.create_image(image_name, *args, **kwgs)
        image = utils.AttrDict(name=image_name)
        images.append(image)
        return image

    yield _create_image

    for image in images:
        images_steps.delete_image(image.name)


@pytest.fixture
def images(request, get_glance_steps, uncleanable, credentials):
    """Fixture to create cirros images with default options.

    Args:
        request (obj): py.test's SubRequest instance
        get_glance_steps (function): function to get glance steps
        uncleanable (AttrDict): data structure with skipped resources
        credentials (object): CredentialsManager instance

    Returns:
        list: AttrDict instances with created images' names
    """
    params = {'count': 1}
    params.update(getattr(request, 'param', {}))
    names = utils.generate_ids('cirros', count=params['count'])
    with create_images_context(get_glance_steps,
                               uncleanable,
                               credentials,
                               names,
                               config.CIRROS_QCOW2_URL) as images:
        yield [utils.AttrDict(name=image['name']) for image in images]


@pytest.fixture
def image(images):
    """Fixture to create cirros images with default options.

    Args:
        images (list): list of created images

    Returns:
        AttrDict: object with created image name
    """
    return images[0]
