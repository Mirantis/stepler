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


@pytest.mark.idempotent_id('7d0916e7-9bc8-449c-a307-f29eedf6dba8',
                           api_version=1)
@pytest.mark.idempotent_id('fb88e71a-1595-4b65-914e-eea200998b22',
                           api_version=2)
@pytest.mark.parametrize('api_version', [1, 2])
def test_download_zero_size_image(glance_steps, cli_glance_steps, api_version):
    """**Scenario:** Verify that zero-size image cannot be downloaded.

    **Steps:**

    #. Run cli command 'glance image-create'
    #. Run cli command 'glance image-download <image_id>'
    #. Check that command is failed with error 'Image is not active'
        (api_version=1) or 'Image has no data' (api_version=2)
    #. Run cli command 'glance image-download <image_id> --progress'
    #. Check that command is failed with error 'Image is not active'
        (api_version=1) or 'Image has no data' (api_version=2)

    **Teardown:**

    #. Delete image
    """
    image = cli_glance_steps.create_image(
        image_name=next(utils.generate_ids()),
        api_version=api_version)[0]

    cli_glance_steps.check_negative_download_zero_size_image(
        image_id=image['id'], progress=False, api_version=api_version)

    cli_glance_steps.check_negative_download_zero_size_image(
        image_id=image['id'], progress=True, api_version=api_version)
