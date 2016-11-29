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

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('85461edd-7c82-4c27-ad19-d3af178818fe',
                           api_version=1)
@pytest.mark.idempotent_id('62e9cf8b-ba28-4ac3-9965-abf758919714',
                           api_version=2)
@pytest.mark.parametrize('api_version', [1, 2])
def test_image_list_contains_created_image(glance_steps,
                                           cli_glance_steps,
                                           api_version):
    """**Scenario:** Check support of unicode symbols in image name.

    **Steps:**

    #. Create image with name 試験画像 with Glance API
    #. Check that created image is in list using CLI

    **Teardown:**

    #. Delete image
    """
    image = glance_steps.create_images(
        image_names=utils.generate_ids(u'試験画像', use_unicode=True),
        image_path=utils.get_file_path(config.CIRROS_QCOW2_URL))[0]
    cli_glance_steps.check_image_list_contains(image=image,
                                               api_version=api_version)


@pytest.mark.idempotent_id('6931aa9c-10df-4c5f-8837-a3090b6e1d57',
                           api_version=1)
@pytest.mark.idempotent_id('26046211-6e00-41b0-ad7c-995340637063',
                           api_version=2)
@pytest.mark.parametrize('api_version', [1, 2])
def test_image_list_doesnt_contain_deleted_image(glance_steps,
                                                 cli_glance_steps,
                                                 api_version):
    """**Scenario:** Check support of unicode symbols in image name.

    **Steps:**

    #. Create image with name 試験画像 with Glance API
    #. Delete image via API
    #. Check that image deleted using CLI command
    """
    image = glance_steps.create_images(
        image_names=utils.generate_ids(u'試験画像', use_unicode=True),
        image_path=utils.get_file_path(config.CIRROS_QCOW2_URL))[0]
    glance_steps.delete_images([image])
    cli_glance_steps.check_image_list_doesnt_contain(image=image,
                                                     api_version=api_version)


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


@pytest.mark.idempotent_id('9290e363-0607-45be-be0a-1e832da59b94',
                           file_option=True)
@pytest.mark.idempotent_id('a4172d9b-38a1-4c18-9cc2-e9eddd514c7d',
                           file_option=False)
@pytest.mark.parametrize('file_option',
                         [True, False],
                         ids=['via file option', 'via stdout redirecting'])
def test_download_glance_image(cirros_image,
                               cli_download_image,
                               glance_steps,
                               file_option):
    """**Scenario:** Download glance image via CLI.

    **Setup:**

    #. Upload cirros image

    **Steps:**

    #. Download cirros image via CLI
    #. Compare md5 of uploaded cirros image and downloaded cirros image

    **Teardown:**

    #. Delete cirros image
    """
    downloaded_image_path = cli_download_image(cirros_image, file_option)
    glance_steps.check_image_hash(utils.get_file_path(config.CIRROS_QCOW2_URL),
                                  downloaded_image_path)


@pytest.mark.idempotent_id('f0a11f9e-b54e-11e6-a750-67737169ac5d',
                           api_version=1)
@pytest.mark.idempotent_id('f46f1db0-b54e-11e6-a5c0-3b21ec537c1f',
                           api_version=2)
@pytest.mark.parametrize('api_version', [1, 2])
def test_negative_remove_deleted_image(glance_steps,
                                       cli_glance_steps,
                                       api_version):
    """**Scenario:** Try to remove already deleted image.

    **Steps:**

    #. Create image
    #. Delete created image
    #. Try to remove deleted image
    """
    image = glance_steps.create_images(
        image_path=utils.get_file_path(config.UBUNTU_QCOW2_URL))[0]

    glance_steps.delete_images([image])
    cli_glance_steps.check_negative_delete_non_existing_image(
        image,
        api_version=api_version)


@pytest.mark.idempotent_id('e790bb42-b631-11e6-a72f-db6c1f65dd0f',
                           api_version=1)
@pytest.mark.idempotent_id('e841a33a-b631-11e6-b970-4769909f93c3',
                           api_version=2)
@pytest.mark.parametrize('api_version', [1, 2])
def test_update_image_property(ubuntu_image,
                               glance_steps,
                               cli_glance_steps,
                               api_version):
    """**Scenario:** Update image property.

    **SetUp:**

    #. Create ubuntu image

    **Steps:**

    #. Update image property
    #. Check that output cli command 'glance image-show <id>'
       contains updated property

    **TearDown:**

    #. Delete ubuntu image
    """
    glance_steps.update_images(images=[ubuntu_image],
                               key='value')
    cli_glance_steps.check_image_property(ubuntu_image,
                                          property_key='key',
                                          property_value='value',
                                          api_version=api_version)
