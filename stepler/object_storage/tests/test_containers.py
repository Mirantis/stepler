"""
-------------------
Swift restart tests
-------------------
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

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('233120d6-e410-436d-955a-4a4f1dcf255d')
@pytest.mark.requires('glance_backend == "swift"')
def test_restart_all_swift_services(
        cirros_image,
        container_steps,
        os_faults_steps,
        glance_steps):
    """**Scenario:** Restart all swift services.

    **Setup:**

    #. Create cirros image

    **Steps:**

    #. Restart all swift services on all controllers
    #. Create new container
    #. Upload data to container
    #. Download data from container
    #. Verify data checksum
    #. Remove data from container
    #. Remove container
    #. Download cirros image
    #. Verify downloaded image file

    **Teardown:**

    #. Delete created containers
    #. Delete created images
    """
    swift_services = os_faults_steps.get_services_names(config.SWIFT)
    os_faults_steps.restart_services(swift_services)
    container_name, object_name, content = utils.generate_ids(count=3)
    container_steps.create(container_name)
    container_steps.put_object(container_name, object_name, content)
    container_steps.check_object_content(container_name, object_name, content)
    container_steps.delete_object(container_name, object_name)
    container_steps.delete(container_name)
    glance_steps.check_image_content(
        cirros_image, utils.get_file_path(config.CIRROS_QCOW2_URL))


@pytest.mark.idempotent_id('7c0f5bef-c1cb-4f54-8096-3122d873e044')
def test_upload_object_to_container(container_steps):
    """**Scenario:** Upload object to container.

    **Setup:**

    #. Create container
    #. Create object
    #. Upload object to container
    #. Check that this object presents into the container

    **Teardown:**

    #. Delete container
    #. Delete object
    """
    container_name, object_name, content = utils.generate_ids(count=3)
    container_steps.create(name=container_name)
    container_steps.put_object(container_name=container_name,
                               object_name=object_name,
                               content=content)
    container_steps.check_object_presence(container_name=container_name,
                                          object_name=object_name)


@pytest.mark.idempotent_id('eb3e4694-95b5-4436-8914-42494d7da217')
def test_remove_object_from_container(container_steps):
    """**Scenario:** Remove object from container.

    **Setup:**

    #. Create container
    #. Create object
    #. Upload object to container
    #. Delete object
    #. Check that object doesn't present in container

    **Teardown:**

    #. Delete container
    #. Delete object
    """
    container_name, object_name, content = utils.generate_ids(count=3)
    container_steps.create(name=container_name)
    container_steps.put_object(container_name=container_name,
                               object_name=object_name,
                               content=content)
    container_steps.delete_object(container_name=container_name,
                                  object_name=object_name)
    container_steps.check_object_presence(container_name=container_name,
                                          object_name=object_name,
                                          must_present=False)


@pytest.mark.idempotent_id('8f5392a4-f427-4133-882b-80497692983a')
def test_container_presents_in_list(container_steps):
    """**Scenario:** Check that container presents into list of containers.

    **Steps:**

    #. Create new container
    #. Check container exists in containers list

    **Teardown:**

    #. Delete container
    """
    container_name = next(utils.generate_ids())
    container_steps.create(name=container_name)


@pytest.mark.idempotent_id('4a00ad6e-51d4-4b65-93ae-e2d198225b71')
def test_container_does_not_present_in_list(container_steps):
    """**Scenario**: Check container doesn't present into list of containers.

    **Steps:**

    #. Create new container
    #. Remove container
    #. Check container doesn't exist in containers list
    """
    container_name = next(utils.generate_ids())
    container_steps.create(container_name)
    container_steps.delete(container_name)


@pytest.mark.idempotent_id('f9fd923d-003f-4130-ae1c-a22de450f9cd')
def test_upload_big_object(container_steps):
    """**Scenario:** Upload big object to Object Storage.

    **Setup:**

    #. Create container
    #. Create object
    #. Upload big object to container
    #. Check that this object presents into the container

    **Teardown:**

    #. Delete container
    #. Delete object
    """
    content_big_file = next(utils.generate_files(size=10**10))
    container_name, object_name = utils.generate_ids(count=2)
    container_steps.create(name=container_name)
    container_steps.put_object(container_name=container_name,
                               object_name=object_name,
                               content=content_big_file)
    container_steps.check_object_presence(container_name=container_name,
                                          object_name=object_name)


@pytest.mark.idempotent_id('03ed9be4-d134-4463-8e4c-c069688209eb')
def test_download_object(container_steps):
    """**Scenario:** Download object from Object Storage.

    **Setup:**

    #. Create container
    #. Create object
    #. Upload object to container
    #. Check that this object presents into the container

    **Steps:**
    #.Upload object from container

    #. Delete container
    #. Delete object
    """

    container_name, file_name, content, object_name = utils.generate_ids(
        count=4)
    container_steps.create(name=container_name)
    created_object = list(utils.generate_files(prefix='test'))[0]
    container_steps.put_object(container_name=container_name,
                               object_name=created_object,
                               content=content)
    downloaded_object = container_steps.get_object_from_container(
        container_name=container_name, object_name=created_object,
        file_name=created_object)
    container_steps.check_object_hash(created_object, downloaded_object)
