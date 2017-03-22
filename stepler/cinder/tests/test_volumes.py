"""
------------
Volume tests
------------
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

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('3421a84f-5a15-4195-ba58-1e143092ef1e')
def test_create_volume_from_snapshot(volume_snapshot, volume_steps):
    """**Scenario:** Verify creation volume from snapshot.

    **Setup:**

    #. Create volume1
    #. Create snapshot from volume1

    **Steps:**

    #. Create volume2 from snapshot
    #. Delete volume2

    **Teardown:**

    #. Delete snapshot
    #. Delete volume1
    """
    volumes = volume_steps.create_volumes(snapshot_id=volume_snapshot.id)
    volume_steps.delete_volumes(volumes)


@pytest.mark.idempotent_id('965cb50a-2900-4788-974f-9def0648484a')
@pytest.mark.parametrize('volumes_count', [10])
def test_create_delete_many_volumes(volume_steps, volumes_count):
    """**Scenario:** Verify that 10 cinder volumes can be created and deleted.

    **Steps:**

    #. Create 10 cinder volumes
    #. Delete 10 cinder volumes

    **Teardown:**

    #. Delete volumes
    """
    volumes = volume_steps.create_volumes(
        names=utils.generate_ids(count=volumes_count))
    volume_steps.delete_volumes(volumes)


@pytest.mark.idempotent_id('45783965-096f-46d6-a863-e466cc9d2d49')
def test_create_volume_without_name(volume_steps):
    """**Scenario:** Verify creation of volume without name.

    **Steps:**

    #. Create volume without name

    **Teardown:**

    #. Delete volume
    """
    volume_steps.create_volumes(names=[None])


@pytest.mark.idempotent_id('8b08bc8f-e1f4-4f6e-8f98-dfcb1f9f538a')
def test_create_volume_description(volume_steps):
    """**Scenario:** Verify creation of volume with description.

    **Steps:**

    #. Create volume without name but with description

    **Teardown:**

    #. Delete volume
    """
    volume_steps.create_volumes(names=[None],
                                description=next(utils.generate_ids()))


@pytest.mark.idempotent_id('56cc7c76-ae92-423d-81ad-8cece5f875ad')
def test_create_volume_description_max(volume_steps):
    """**Scenario:** Verify creation of volume with max description length.

    **Steps:**

    #. Create volume with description length == max(255)

    **Teardown:**

    #. Delete volume
    """
    volume_steps.create_volumes(
        description=next(utils.generate_ids(length=255)))


@pytest.mark.idempotent_id('978a580d-22c3-4e98-8ff9-7ff8541cdd48',
                           size=0)
@pytest.mark.idempotent_id('3610f889-15ff-43a2-9678-6375f1621f7c',
                           size=-1)
@pytest.mark.idempotent_id('65fe505b-d526-4d05-a77a-b94c129314ec',
                           size='')
@pytest.mark.idempotent_id('8b9fa581-19bb-41ac-bb97-c8eb21f7fa98',
                           size=' ')
@pytest.mark.idempotent_id('8c725286-cd52-4c3f-8abb-1e38109041aa',
                           size='abc')
@pytest.mark.idempotent_id('1f2a2eb8-5d10-4021-b2b1-483766698c37',
                           size='*&^%$%')
@pytest.mark.parametrize('size', [0, -1, '', ' ', 'abc', '*&^%$%'])
def test_create_volume_wrong_size(volume_steps, size):
    """**Scenario:** Verify creation of volume with zero/negative size.

    **Steps:**

    #. Create volume with size 0/-1 Gbs
    #. Check that BadRequest occurred
    """
    volume_steps.check_volume_not_created_with_incorrect_size(size=size)


@pytest.mark.idempotent_id('331ef3fb-f048-4684-bf78-433923ab4a48')
def test_create_volume_max_size(volume_size_quota, volume_steps):
    """**Scenario:** Verify creation of volume with max volume size.

    **Setup:**

    #. Set required max volume size quota

    **Steps:**

    #. Create volume with max volume size
    #. Check that volume is available

    **Teardown:**

    #. Delete volume
    #. Set max volume size quota to its initial value
    """
    volume_steps.create_volumes(size=volume_size_quota)


@pytest.mark.idempotent_id('ed2a92fc-356c-4ae5-835b-99a9ce4d8fe0')
def test_create_volume_more_max_size(volume_size_quota, volume_steps):
    """**Scenario:** Verify creation of volume with size more than max.

    **Setup:**

    #. Set required max volume size quota

    **Steps:**

    #. Try to create volume with bigger size than max volume size
    #. Check that creation is failed
    #. Check error message

    **Teardown:**

    #. Set max volume size quota to its initial value
    """
    volume_steps.check_volume_not_created_with_size_more_than_limit(
        size=volume_size_quota + 1)


@pytest.mark.idempotent_id('bcd12002-dfd3-44c9-b270-d844d61a009c')
def test_negative_create_volume_name_long(volume_steps):
    """**Scenario:** Verify creation of volume with name length > 255.

    **Steps:**

    #. Try to create volume with name length > 255
    #. Check that BadRequest exception raised
    """
    volume_steps.check_volume_not_created_with_long_name(
        name=next(utils.generate_ids(length=256)))


@pytest.mark.idempotent_id('34ca65a0-a254-49c5-8157-13e11c88a5b3')
def test_negative_create_volume_non_exist_volume_type(cirros_image,
                                                      volume_steps):
    """**Scenario:** Can't create volume from image with fake volume type.

    **Setup:**

    #. Create cirros image

    **Steps:**

    #. Try to create volume from image using non existed volume type
    #. Check that NotFound exception raised

    **Teardown:**

    #. Delete cirros image
    """
    volume_steps.check_volume_not_created_with_non_exist_volume_type(
        cirros_image)


@pytest.mark.idempotent_id('ee218b6e-7f61-43cd-a87e-00bf5edfe258')
def test_negative_create_volume_wrong_image_id(volume_steps):
    """**Scenario:** Verify creation of volume with wrong image id.

    **Steps:**

    #. Try to create volume with wrong image id
    #. Check that BadRequest exception raised
    """
    volume_steps.check_volume_not_created_with_wrong_image_id()


@pytest.mark.idempotent_id('f2e90086-42d7-4257-96ef-10ca5ea3a4c3')
def test_create_volume_from_volume(volume, volume_steps):
    """**Scenario:** Verify creation of volume from volume.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume2 from volume

    **Teardown:**

    #. Delete volume2
    #. Delete volume
    """
    volume_steps.create_volumes(source_volid=volume.id)


@pytest.mark.idempotent_id('ac8eba2e-7cb1-4a90-af7f-0179affaeeb4')
def test_delete_volume_cascade(volume, volume_steps, snapshot_steps):
    """**Scenario:** Verify volume deletion with cascade option.

    **Steps:**

    #. Create volume
    #. Create volume snapshot
    #. Delete volume with cascade option
    #. Check that snapshot is deleted too
    """
    snapshot_name = next(utils.generate_ids('snapshot'))
    snapshots = snapshot_steps.create_snapshots(volume, [snapshot_name])
    volume_steps.delete_volumes([volume], cascade=True)
    snapshot_steps.check_snapshots_presence(snapshots, must_present=False)


@pytest.mark.idempotent_id('fbcb9a58-9a4d-4864-88db-c08a14475994')
def test_negative_delete_volume_cascade(volume,
                                        volume_snapshot,
                                        volume_steps,
                                        snapshot_steps):
    """**Scenario:** Verify volume deletion without cascade option.

    **Setup:**

    #. Create volume
    #. Create volume snapshot

    **Steps:**

    #. Try to delete volume without cascade option
    #. Check that BadRequest exception raised
    #. Check that volume is present
    #. Check that snapshot is present

    **Teardown:**

    #. Delete snapshot
    #. Delete volume
    """
    volume_steps.check_volume_deletion_without_cascading_failed(volume)
    snapshot_steps.check_snapshots_presence([volume_snapshot],
                                            must_present=True)


@pytest.mark.idempotent_id('541b506a-fc7b-4902-b60e-1b6cbaf27636')
def test_negative_delete_volume_wrong_id(volume_steps):
    """**Scenario:** Verify volume deletion with wrong volume id.

    **Steps:**

    #. Try to delete volume with wrong volume id
    #. Check that NotFound exception raised
    """
    volume_steps.check_volume_deletion_with_wrong_id()


@pytest.mark.requires(
    'cinder_nodes_count >= 2 and cinder_storage_protocol != "ceph"')
@pytest.mark.idempotent_id('f0c407a3-7aa1-400c-9a9f-6c69870e3fb9')
def test_migrate_volume(volume, volume_steps, os_faults_steps):
    """**Scenario:** Migrate volume to another host.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Find cinder volume host to migrate
    #. Migrate cinder volume

    **Teardown:**

    #. Delete volume
    """
    cinder_nodes = os_faults_steps.get_nodes(
        service_names=[config.CINDER_VOLUME])
    migration_host = volume_steps.get_volume_migrate_host(volume, cinder_nodes)
    volume_steps.migrate_volume(volume, migration_host)


@pytest.mark.idempotent_id('2f740550-479e-4a23-a710-7d330382b140')
def test_volumes_list(volume_steps):
    """**Scenario:** Request list of volumes.

    **Steps:**

    #. Get list of volumes
    """
    volume_steps.get_volumes(check=False)
