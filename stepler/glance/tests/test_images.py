# -*- coding: utf-8 -*-

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


@pytest.mark.idempotent_id('85461edd-7c82-4c27-ad19-d3af178818fe')
def test_validate_glance_unicode_support(glance_steps_v1):
    """**Scenario:** Check support of unicode symbols in image name.

    **Steps:**

        #. Create image with name 試験画像
        #. Check that created image is in list and has status `queued`
        #. Delete image
        #  Check that image deleted
    """
    image_name = u"試験画像"
    image = glance_steps_v1.create_image(image_name=image_name,
                                         image_path=utils.get_file_path
                                         (config.UBUNTU_QCOW2_URL))

    images_list = glance_steps_v1.list_images()
    assert image in images_list
    assert image.status == 'queued'

    glance_steps_v1.delete_image(image)
    assert image not in images_list
