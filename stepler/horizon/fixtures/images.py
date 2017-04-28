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
from stepler.horizon import steps
from stepler.third_party import utils

__all__ = [
    'horizon_images',
    'horizon_image',
    'images_steps_ui',
]


@pytest.fixture
def images_steps_ui(glance_steps, login, horizon):
    """Fixture to get images steps.

    glance_steps instance is used for images cleanup.

    Args:
        glance_steps (GlanceSteps): instantiated glance steps
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.ImagesSteps: instantiated UI images steps
    """
    return steps.ImagesSteps(horizon)


@pytest.fixture
def horizon_images(request, get_glance_steps, uncleanable, credentials):
    """Fixture to create cirros images with default options.

    Args:
        request (object): py.test's SubRequest instance
        get_glance_steps (function): function to get glance steps
        uncleanable (AttrDict): data structure with skipped resources
        credentials (object): CredentialsManager instance

    Returns:
        list: images list
    """
    params = {'count': 1}
    params.update(getattr(request, 'param', {}))
    names = utils.generate_ids('cirros', count=params['count'])
    with create_images_context(get_glance_steps,
                               uncleanable,
                               credentials,
                               names,
                               config.CIRROS_QCOW2_URL) as images:
        yield images


@pytest.fixture
def horizon_image(horizon_images):
    """Fixture to create cirros image with default options.

    Args:
        horizon_images (list): list of created images

    Returns:
        object: glance image
    """
    return horizon_images[0]
