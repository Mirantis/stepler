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
                           api_version=1, progress=False)
@pytest.mark.idempotent_id('2aa49178-d626-466f-a074-0f6aadc86739',
                           api_version=1, progress=True)
@pytest.mark.idempotent_id('fb88e71a-1595-4b65-914e-eea200998b22',
                           api_version=2, progress=False)
@pytest.mark.idempotent_id('c3de7fdc-7453-4700-b692-461da142d4b4',
                           api_version=2, progress=True)
@pytest.mark.parametrize('api_version, progress', [(1, False), (1, True),
                                                   (2, False), (2, True)])
def test_download_zero_size_image(glance_steps,
                                  cli_glance_steps,
                                  api_version,
                                  progress):
    """**Scenario:** Verify that zero-size image can't be downloaded.

    **Steps:**

    #. Create a zero-size image
    #. Run cli command 'glance image-download <image_id>' without/with
       option '--progress'
    #. Check that command is failed with error 'Image is not active'
        (api_version=1) or 'Image has no data' (api_version=2)

    **Teardown:**

    #. Delete image
    """
    image = glance_steps.create_images(image_path=None,
                                       disk_format=None,
                                       container_format=None,
                                       upload=False)[0]

    cli_glance_steps.check_negative_download_zero_size_image(
        image_id=image['id'],
        progress=progress,
        api_version=api_version)


@pytest.mark.idempotent_id('54bdc370-45f6-4085-977c-07996fb81943',
                           api_version=1)
@pytest.mark.idempotent_id('30537390-e1ba-47bc-aca0-db94a740f728',
                           api_version=2)
@pytest.mark.parametrize('api_version', [1, 2])
def test_project_in_image_member_list(cirros_image,
                                      project,
                                      cli_glance_steps,
                                      glance_steps,
                                      api_version):
    """**Scenario:** Verify 'glance member-list' command.

    Test checks that 'glance member-list --image_id <id>' shows bound project.

    **Setup:**

    #. Create cirros image
    #. Create non-admin project

    **Steps:**

    #. Bind project to image via API
    #. Check cli command 'glance member-list --image_id <id>' shows bound
        project

    **Teardown:**

    #. Delete project
    #. Delete cirros image
    """
    glance_steps.bind_project(cirros_image, project, check=False)
    cli_glance_steps.check_project_in_image_member_list(
        cirros_image, project, api_version=api_version)


@pytest.mark.idempotent_id('885ce1ec-ad7d-4401-b67d-14b5f2451674',
                           api_version=1)
@pytest.mark.idempotent_id('3adc71e3-2362-4a95-aac6-93a14da65487',
                           api_version=2)
@pytest.mark.parametrize('api_version', [1, 2])
def test_create_image_member(cirros_image,
                             project,
                             cli_glance_steps,
                             glance_steps,
                             api_version):
    """**Scenario:** Verify 'glance member-create' command.

    **Setup:**

    #. Create cirros image
    #. Create non-admin project

    **Steps:**

    #. Run cli command 'glance member-create <image_id> <project_id>'
    #. Check that project is in image member-list via API

    **Teardown:**

    #. Delete project
    #. Delete cirros image
    """
    cli_glance_steps.create_image_member(cirros_image, project,
                                         api_version=api_version)
    glance_steps.check_image_bind_status(cirros_image, project)


@pytest.mark.idempotent_id('41594846-bf76-4132-9d80-3cb679b12516',
                           api_version=1)
@pytest.mark.idempotent_id('e2393652-ae09-42ae-87fd-7b16adeaa6f7',
                           api_version=2)
@pytest.mark.parametrize('api_version', [1, 2])
def test_delete_image_member(cirros_image,
                             project,
                             cli_glance_steps,
                             glance_steps,
                             api_version):
    """**Scenario:** Verify 'glance member-delete' command.

    **Setup:**

    #. Create cirros image
    #. Create non-admin project

    **Steps:**

    #. Bind project to image via API
    #. Run cli command 'glance member-delete <image_id> <project_id>'
    #. Check that project not in image member-list via API

    **Teardown:**

    #. Delete project
    #. Delete cirros image
    """
    glance_steps.bind_project(cirros_image, project)
    cli_glance_steps.delete_image_member(cirros_image, project,
                                         api_version=api_version)
    glance_steps.check_image_bind_status(cirros_image, project, bound=False)


@pytest.mark.idempotent_id('9290e363-0607-45be-be0a-1e832da59b94')
def test_download_glance_image(cirros_image,
                               cli_download_image,
                               glance_steps):
    """**Scenario:** Download glance image via CLI.

    **Setup:**

    #. Create cirros image

    **Steps:**

    #. Download cirros image via CLI
    #. Compare md5 of cirros image and downloaded image

    **Teardown:**

    #. Delete cirros image
    """
    downloaded_path = cli_download_image(cirros_image)
    glance_steps.check_image_hash(cirros_image, downloaded_path)
