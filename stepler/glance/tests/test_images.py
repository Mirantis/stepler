"""
-----------
Image tests
-----------
"""

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


@pytest.mark.idempotent_id('beabc5e4-6de4-4aff-8c4a-5bf07df6c5a0')
def test_big_image_create_delete(glance_steps):
    """**Scenario:**Check big image creation and deletion from file.

    **Steps:**

        #. Create file 25Gb
        #. Create image from this file
        #. Delete image

    **Teardown:**

        #. Delete big file
    """
    size = 1024 * 1024 * 1024 * 25
    with utils.generate_file_context(size=size) as big_file_path:
        image = glance_steps.create_image(
            image_name=next(utils.generate_ids('image')),
            image_path=big_file_path)
        glance_steps.delete_image(image)
