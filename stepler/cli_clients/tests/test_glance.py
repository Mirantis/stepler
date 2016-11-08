"""
-------------------------
Tests for glance CLI client
-------------------------
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
from hamcrest import *


@pytest.mark.idempotent_id('9290e363-0607-45be-be0a-1e832da59b94')
def test_validate_glance_image(cli_glance_steps):
    """**Scenario:** Validate Glance image (upload/download, compare md5-sum
    of image).

    **Steps:**

    #. download image to disk via wget or generate a payload image
    #. create image
    #. download image
    #. compare md5sum

    **Teardown:**

    #. Delete image
    """
    file_name = cli_glance_steps.create_file(size=1024)
    uploaded_image_id = cli_glance_steps.get_image_id(file_name)
    downloaded_image_name = cli_glance_steps.create_file()
    cli_glance_steps.download_image(uploaded_image_id, downloaded_image_name)
    md5sum_first = cli_glance_steps.md5(file_name)
    md5sum_second = cli_glance_steps.md5(downloaded_image_name)
    assert_that(md5sum_first, equal_to(md5sum_second))
    cli_glance_steps.delete_image(uploaded_image_id)
    cli_glance_steps.delete_file(file_name)
    cli_glance_steps.delete_file(downloaded_image_name)
