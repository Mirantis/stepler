"""
-----------
Image tests
-----------
"""

#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('1b1a0953-a772-4cfe-a7da-2f6de950eede')
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


@pytest.mark.idempotent_id('b0605804-9aa1-11e6-bc0e-5b4a274fc90f')
def test_negative_remove_deleted_image_v2(glance_steps_v2):
    """**Scenario:**Try to remove deleted image.

    **Steps:**

        #. Create image
        #. Delete created image
        #. Try to remove deleted image

    """
    image = glance_steps_v2.create_image(
        image_name=next(utils.generate_ids('image')),
        image_path=utils.get_file_path(config.UBUNTU_QCOW2_URL))

    glance_steps_v2.delete_image(image)
    glance_steps_v2.check_delete_non_existing_image(image=image)
