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


@pytest.mark.testrail_id(1680099)
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


def test_change_image_status_directly(cirros_image, auth_steps, glance_steps):
    """**Scenario:** Verify that user can't change image status directly with
        v1 API.

    **Note:**

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
    auth_headers = auth_steps.get_auth_headers()
    glance_steps.send_put_request(
        cirros_image,
        auth_headers, {'x-image-meta-status': 'queued'},
        check=False)
    glance_steps.check_image_status(cirros_image, 'active')
