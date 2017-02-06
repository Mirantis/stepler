"""
--------------------------
Tests for swift CLI client
--------------------------
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


@pytest.mark.idempotent_id('0f055e9b-1caa-4f86-ab99-c1d51e4978c7')
def test_containers_list_contains_created_container(cli_swift_steps,
                                                    container_steps):
    """**Scenario:** Check container list contains created container.

    **Steps:**

    #. Create container via Swift API
    #. Check that created container is in list using CLI

    **Teardown:**

    #. Delete container
    """
    container_name = next(utils.generate_ids())
    container_steps.create(name=container_name)
    cli_swift_steps.check_container_presence(container_name)


@pytest.mark.idempotent_id('eb1e03e4-e0b4-42b8-8a8f-36d500929639')
def test_delete_container(cli_swift_steps, container_steps):
    """**Scenario**: Check container have been deleted successfully.

    **Steps:**

    #. Create container via Swift API
    #. Remove this container using Swift CLI
    """
    container_name = next(utils.generate_ids())
    container_steps.create(name=container_name)
    cli_swift_steps.delete(container_name)


@pytest.mark.idempotent_id('f715705b-bfe6-4ea6-971f-27833168f53e')
def test_containers_list_doesnt_contain_deleted_container(cli_swift_steps,
                                                          container_steps):
    """**Scenario:** Check container list doesn't contain deleted container.

    **Steps:**

    #. Create container via Swift API
    #. Delete container using Swift API
    #. Check that deleted container does not exist in list of containers
    via CLI
    """
    container_name = next(utils.generate_ids())
    container_steps.create(name=container_name)
    container_steps.delete(name=container_name)
    cli_swift_steps.check_container_presence(
        container_name=container_name, must_present=False)


@pytest.mark.idempotent_id('0f0482b3-0b87-4e47-8ef6-de4bb51d8c04')
def test_upload_object_cli(cli_swift_steps, container_steps):
    """**Scenario:** Check object uploads to container successfully.

    **Steps:**

    #. Create container via Swift API
    #. Create object to upload to container
    #. Upload this object to container using CLI

    **Teardown:**

    #. Delete container
    #. Delete object
    """
    container_name, object_name = utils.generate_ids(count=2)
    container_steps.create(name=container_name)
    cli_swift_steps.upload(container_name=container_name,
                           object_name=object_name)


@pytest.mark.idempotent_id('2da956c3-8715-4ba0-ae33-8e6d524ce9fe')
def test_upload_object_to_container(cli_swift_steps, container_steps):
    """**Scenario:** Check object uploaded to container successfully.

    **Steps:**

    #. Create container via Swift API
    #. Create object to upload to container
    #. Upload this object to container using API
    #. Check this object exists inside the container

    **Teardown:**

    #. Delete container
    #. Delete this object
    """
    container_name, object_name, content = utils.generate_ids(count=3)
    container_steps.create(name=container_name)
    container_steps.put_object(container_name=container_name,
                               object_name=object_name,
                               content=content)
    cli_swift_steps.check_object_in_container(container_name=container_name,
                                              object_name=object_name)
