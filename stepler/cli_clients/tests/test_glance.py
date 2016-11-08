"""
----------------
Glance CLI tests
----------------
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

from hamcrest import assert_that
from hamcrest import equal_to

from stepler.third_party import utils


@pytest.mark.idempotent_id('b5948a9d-a0a2-40ca-9638-554020dcde80',
                           api_version=1)
@pytest.mark.idempotent_id('928a6294-d172-4c7a-afc1-5e0fa772caf4',
                           api_version=2)
@pytest.mark.parametrize('api_version', [1, 2])
def test_upload_image_without_properties(cli_glance_steps, api_version):
    """**Scenario:** Verify image is not created from file without properties.

    Test checks image from file can't be created without disk-format and
    container-format

    **Steps:**

    #. Run cli command 'glance image-create --file <filename>'
    #. Check that command failed with expected error message
    """
    cli_glance_steps.check_negative_image_create_without_properties(
        filename=next(utils.generate_ids()), api_version=api_version)


@pytest.mark.idempotent_id('9290e363-0607-45be-be0a-1e832da59b94')
@pytest.mark.usefixtures('images_cleanup')
@pytest.mark.usefixtures('delete_file')
def test_generate_glance_image(glance_steps, cli_glance_steps, cirros_image):
    """**Scenario:** Validate Glance image (upload/download, compare md5-sum

    of image).

    **Steps:**

    #. download image to disk via wget or generate a payload image
    #. create image
    #. download image
    #. compare md5sum

    **Teardown:**

    #. Delete image
    #. Delete file
    """
    md5sum_cirros = cli_glance_steps.check_md5sum(cirros_image)
    uploaded_image_id = glance_steps.create_images_from_file(
        cirros_image, image_names=None, disk_format='qcow2',
        container_format='bare', check=True)
    downloaded_image_name = cli_glance_steps.create_file()
    cli_glance_steps.download_image(uploaded_image_id[0],
                                    downloaded_image_name)
    md5sum_cirros_downloaded = cli_glance_steps.check_md5sum(
        downloaded_image_name)
    assert_that(md5sum_cirros, equal_to(md5sum_cirros_downloaded))
