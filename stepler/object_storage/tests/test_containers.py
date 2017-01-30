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


@pytest.mark.idempotent_id('8f5392a4-f427-4133-882b-80497692983a')
def test_container_presents_in_list(container_steps):
    """**Scenario:** Check that container created and present into list
    of containers

    **Steps:**

    #. Create new container
    #. Check container exist in containers list

    **Teardown:**

    #. Delete container
    """
    container_name = next(utils.generate_ids())
    container_steps.create(name=container_name)
    container_steps.check_presence(name=container_name)


@pytest.mark.idempotent_id('4a00ad6e-51d4-4b65-93ae-e2d198225b71')
def test_container_does_not_present_in_list(container_steps):
    """**Scenario**: Check that container deleted and not present into list
    of containers

    **Steps:**

    #. Create new container
    #. Remove container
    #. Check container doesn't exist in containers list
    """
    container_name = next(utils.generate_ids())
    container_steps.create(name=container_name)
    container_steps.delete(name=container_name)
    container_steps.check_presence(name=container_name,
                                   must_present=False)
