# -*- coding: utf-8 -*-

"""
---------------------------
Tests for glance CLI client
---------------------------
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

from stepler.third_party import utils


@pytest.mark.idempotent_id('85461edd-7c82-4c27-ad19-d3af178818fe')
def test_validate_unicode_support(cli_glance_steps):
    """** Scenario: ** Check support of unicode symbols in image name.

    ** Steps: **

    #. Create image with name 試験画像
    #. Check that created image is in list and has status `queued`
    #. Delete image
    #. Check that image deleted
    """
    cli_glance_steps.check_unicode_support()


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
