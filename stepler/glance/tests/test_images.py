"""
-----------
Image tests
-----------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('95c581e9-6b5f-4547-993e-ef1ab19cc29f')
def test_share_glance_image(ubuntu_image, project, glance_steps):
    """**Scenario:** Check sharing glance image to another project.

    **Setup:**

    #. Create ubuntu image
    #. Create project

    **Steps:**

    #. Bind another project to image
    #. Unbind project from image

    **Teardown:**

    #. Delete project
    #. Delete ubuntu image
    """
    glance_steps.bind_project(ubuntu_image, project)
    glance_steps.unbind_project(ubuntu_image, project)


@pytest.mark.idempotent_id('1b1a0953-a772-4cfe-a7da-2f6de950eede')
def test_change_image_status_directly(glance_steps, api_glance_steps_v1):
    """**Scenario:** Verify that user can't change image status directly.

    This test verify that user can't change image status directly with v1 API.

    Note:
        This test verify bug #1496798.

    **Setup:**

    #. Create cirros image

    **Steps:**

    #. Get token
    #. Send PUT request to glance image endpoint with
        {'x-image-meta-status': 'queued'} headers
    #. Check that image's status is still active

    **Teardown:**

    #. Delete cirros image
    """
    images = glance_steps.create_images(
        image_path=utils.get_file_path(config.CIRROS_QCOW2_URL))
    api_glance_steps_v1.update_images(images,
                                      status=config.STATUS_QUEUED,
                                      check=False)
    glance_steps.check_image_status(images[0], config.STATUS_ACTIVE)
