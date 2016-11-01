"""
------------
Backup tests
------------
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


@pytest.mark.idempotent_id('03e63f1b-38e4-48df-a30b-19f796f6ded0')
def test_create_volume_snapshot_backup(volume, volume_snapshot, create_backup):
    """**Scenario:** Verify ability to create backup from snapshot of volume.

    **Setup:**

    #. Create volume
    #. Create volume snapshot

    **Steps:**

    #. Create backup

    **Teardown:**

    #. Delete snapshot
    #. Delete volume
    #. Delete backup
    """
    create_backup(volume, snapshot_id=volume_snapshot.id)


@pytest.mark.idempotent_id('8d7b0a61-5f94-4fb9-8508-5b00680dc292')
def test_create_volume_backup_with_container(volume,
                                             create_backup,
                                             backup_steps):
    """**Scenario:** Verify volume backup creation with custom container.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create backup with custom container name
    #. Check container name of backup

    **Teardown:**

    #. Delete backup
    #. Delete volume
    """
    container_name = next(utils.generate_ids('container'))
    backup = create_backup(volume, container=container_name)
    backup_steps.check_backup_container(backup, container_name)


@pytest.mark.idempotent_id('87dbe58f-2160-4c9e-833d-d5790d7a9206')
def test_negative_create_backup_long_container_name(volume, backup_steps):
    """**Scenario:** Verify backup creation with too long container name.

    **Setup:**

    #. Create cinder volume

    **Steps:**

    #. Try to create volume backup with container name length > 255
    #. Check that BadRequest exception raised

    **Teardown:**

    #. Delete cinder volume
    """
    long_container_name = next(utils.generate_ids(length=256))
    backup_steps.check_backup_not_created_with_long_container_name(
        volume, container=long_container_name)
