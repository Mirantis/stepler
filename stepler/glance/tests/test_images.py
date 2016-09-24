"""
-----------
Image tests
-----------

@author: schipiga@mirantis.com
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


# TODO: Remove test_upload_image because steps of current test is executed
# in another test scenarios
#@pytest.mark.testrail_id('XXXXX')
def test_upload_image(ubuntu_image):
    """Check that image can be uploaded."""


#@pytest.mark.testrail_id('XXXXX')
def test_share_glance_image(ubuntu_image, project, glance_steps):
    """Check sharing glance image to another project.

    Scenario:
        1. Create image from `image_file`
        2. Check that image is present in list and image status is `active`
        3. Bind another project to image
        4. Check that binded project id is present in image member list
        5. Unbind project from image
        6. Check that project id is not present in image member list
        7. Delete image
        8. Check that image deleted

    """
    glance_steps.bind_project(ubuntu_image, project)
    glance_steps.unbind_project(ubuntu_image, project)
