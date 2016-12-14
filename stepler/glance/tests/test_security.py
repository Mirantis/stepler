"""
---------------------
Glance security tests
---------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import time

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('c30299b4-4f60-4078-962e-5a29c35084ec',
                           api_version='1')
@pytest.mark.idempotent_id('c8c71538-4f98-4c05-b769-9da26796b01f',
                           api_version='2')
@pytest.mark.usefixtires('set_glance_storage_to_file_with_quota')
@pytest.mark.parametrize('api_version', ['1', '2'], ids=['api_v1', 'api_v2'])
def test_user_storage_quota_bypass(get_glance_steps,
                                   os_faults_steps,
                                   api_version):
    """**Scenario:** Check user can't bypass quota with deleting images.

    Note:
        This test verifies bug #1414685

    **Setup:**

    #. Set 'file' storage on glance-api.conf
    #. Set 'user_storage_quota' to 604979776 on glance-api.conf (a little more
        than the size of the image)
    #. Restart glance-api service

    **Steps:**

    #. Create ubuntu image without uploading
    #. Start upload image file in background
    #. Wait few seconds
    #. Delete created image
    #. Repeat steps above 10 times
    #. Wait for all uploads to be done
    #. Check that glance disk usage is not exceed quota

    **Teardown:**

    #. Restore original glance config
    #. Restart glance-api
    """
    glance = get_glance_steps(version=api_version, is_api=False)
    image_path = utils.get_file_path(config.UBUNTU_QCOW2_URL)
    glance_nodes = os_faults_steps.get_nodes(service_names=[config.GLANCE_API])
    processes = []
    for _ in range(10):
        image, = glance.create_images(image_path=None, upload=False)
        p = utils.background(glance.upload_image, image, image_path)
        processes.append(p)
        time.sleep(2)
        glance.delete_images([image])
    for p in processes:
        utils.join_process(p)
    os_faults_steps.check_glance_fs_usage(
        glance_nodes, quota=config.GLANCE_USER_STORAGE_QUOTA)
