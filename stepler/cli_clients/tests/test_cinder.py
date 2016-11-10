"""
---------------------------
Tests for cinder CLI client
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


@pytest.mark.idempotent_id('79d599b8-4b3c-4fc9-84bd-4b6353816d4d')
def test_change_volume_name_non_unicode(volume,
                                        cli_cinder_steps,
                                        volume_steps):
    """**Scenario:** Change volume name with non unicode symbols.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Change volume name with non unicode symbols using CLI
    #. Check that volume name was changed

    **Teardown:**

    #. Delete volume
    """
    cli_cinder_steps.rename_volume(volume, name=config.UNICODE_SYMBOLS)
    volume_steps.check_volume_properties(volume, name=config.UNICODE_SYMBOLS)


@pytest.mark.idempotent_id('a57d8603-b46a-45df-bd75-ef4b6caa433e')
def test_change_volume_description_non_unicode(volume,
                                               cli_cinder_steps,
                                               volume_steps):
    """**Scenario:** Change volume description with non unicode symbols.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Change volume description with non unicode symbols using CLI
    #. Check that volume description was changed

    **Teardown:**

    #. Delete volume
    """
    cli_cinder_steps.rename_volume(volume, description=config.UNICODE_SYMBOLS)
    volume_steps.check_volume_properties(volume,
                                         description=config.UNICODE_SYMBOLS)


@pytest.mark.idempotent_id('225d218b-6562-431d-bdf9-0ec0221c0f86')
def test_volume_backup_non_unicode_name(volume, cli_cinder_steps, backup_steps):
    """**Scenario:** Create volume backup with non unicode symbols name.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume backup with non unicode symbols name using CLI
    #. Check that backup status is available

    **Teardown:**

    #. Delete volume backup
    #. Delete volume
    """
    backup_dict = cli_cinder_steps.create_volume_backup(
        volume, name=config.UNICODE_SYMBOLS)
    backup_steps.check_backup_status(backup_dict['id'],
                                     config.STATUS_AVAILABLE,
                                     timeout=config.BACKUP_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('c64aa74b-990b-43df-8030-4657556e72ee')
def test_show_backup_non_unicode_name(volume, create_backup, cli_cinder_steps):
    """**Scenario:** Show volume backup with non unicode name.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume backup with non unicode name using API
    #. Check CLI command ``cinder backup-show <backup id>``

    **Teardown:**

    #. Delete volume backup
    #. Delete volume
    """
    backup = create_backup(volume, name=config.UNICODE_SYMBOLS)
    cli_cinder_steps.show_volume_backup(backup)


@pytest.mark.idempotent_id('3b6eea01-cd4e-4a6c-bb68-a260650c6dae')
def test_show_backup_non_unicode_description(volume,
                                             create_backup,
                                             cli_cinder_steps):
    """**Scenario:** Show volume backup with non unicode description.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume backup with non unicode description using API
    #. Check CLI command ``cinder backup-show <backup id>``

    **Teardown:**

    #. Delete volume backup
    #. Delete volume
    """
    backup = create_backup(volume, description=config.UNICODE_SYMBOLS)
    cli_cinder_steps.show_volume_backup(backup)


@pytest.mark.idempotent_id('07eb81c1-ca1f-4c65-93c4-f3378e62adfd')
def test_volume_backup_non_unicode_description(volume, cli_cinder_steps,
                                               backup_steps):
    """**Scenario:** Create volume backup with non unicode symbols description.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume backup with non unicode symbols description using CLI
    #. Check that backup status is available

    **Teardown:**

    #. Delete volume backup
    #. Delete volume
    """
    backup_dict = cli_cinder_steps.create_volume_backup(
        volume, description=config.UNICODE_SYMBOLS)
    backup_steps.check_backup_status(backup_dict['id'],
                                     config.STATUS_AVAILABLE,
                                     timeout=config.BACKUP_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('107affa2-fc40-4c7e-8b11-cc1940bd7259')
def test_volume_snapshot_non_unicode_name(volume, cli_cinder_steps,
                                          snapshot_steps):
    """**Scenario:** Create snapshot with non unicode symbols name.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume snapshot with non unicode symbols name using CLI
    #. Check that snapshot status is available

    **Teardown:**

    #. Delete volume snapshot
    #. Delete volume
    """
    snapshot_dict = cli_cinder_steps.create_volume_snapshot(
        volume, name=config.UNICODE_SYMBOLS)
    snapshot_steps.check_snapshots_status(
        [snapshot_dict['id']],
        config.STATUS_AVAILABLE,
        timeout=config.SNAPSHOT_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('98c66ba5-7932-45eb-86f9-9d76ae72851f')
def test_volume_snapshot_non_unicode_description(volume, cli_cinder_steps,
                                                 snapshot_steps):
    """**Scenario:** Create snapshot with non unicode symbols description.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume snapshot with non unicode symbols description
        using CLI
    #. Check that snapshot status is available

    **Teardown:**

    #. Delete volume snapshot
    #. Delete volume
    """
    snapshot_dict = cli_cinder_steps.create_volume_snapshot(
        volume, description=config.UNICODE_SYMBOLS)
    snapshot_steps.check_snapshots_status(
        [snapshot_dict['id']],
        config.STATUS_AVAILABLE,
        timeout=config.SNAPSHOT_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('1237fdcd-abca-4976-aa44-d31fbb4e54c4')
def test_show_snapshot_non_unicode_name(volume, snapshot_steps,
                                        cli_cinder_steps):
    """**Scenario:** Show volume snapshot with non unicode name.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume snapshot with non unicode name using API
    #. Check CLI command ``cinder snapshot-show <snapshot id>``

    **Teardown:**

    #. Delete volume snapshot
    #. Delete volume
    """
    snapshot = snapshot_steps.create_snapshots(
        volume, names=[config.UNICODE_SYMBOLS])[0]
    cli_cinder_steps.show_volume_snapshot(snapshot)


@pytest.mark.idempotent_id('d6816d3b-0035-463e-9980-432df0d65cad')
def test_show_snapshot_non_unicode_description(volume, snapshot_steps,
                                               cli_cinder_steps):
    """**Scenario:** Show volume snapshot with non unicode description.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume snapshot with non unicode description using API
    #. Check CLI command ``cinder snapshot-show <snapshot id>``

    **Teardown:**

    #. Delete volume snapshot
    #. Delete volume
    """
    snapshot = snapshot_steps.create_snapshots(
        volume, description=config.UNICODE_SYMBOLS)[0]
    cli_cinder_steps.show_volume_snapshot(snapshot)


@pytest.mark.idempotent_id('955c4976-ddc7-4d8d-b5c6-1c2bc991af39')
def test_volume_backup_non_unicode_container(volume, cli_cinder_steps,
                                             backup_steps):
    """**Scenario:** Create volume backup with non unicode container name.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume backup with non unicode container name using CLI
    #. Check that backup status is available

    **Teardown:**

    #. Delete volume backup
    #. Delete volume
    """
    backup_dict = cli_cinder_steps.create_volume_backup(
        volume, container=config.UNICODE_SYMBOLS)
    backup_steps.check_backup_status(backup_dict['id'],
                                     config.STATUS_AVAILABLE,
                                     timeout=config.BACKUP_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('815f7bf8-05e7-4556-ac46-8df267c91c75')
def test_show_backup_non_unicode_container_name(volume,
                                                create_backup,
                                                cli_cinder_steps):
    """**Scenario:** Show volume backup with non unicode container name.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume backup with non unicode container name using API
    #. Check CLI command ``cinder backup-show <backup id>``

    **Teardown:**

    #. Delete volume backup
    #. Delete volume
    """
    backup = create_backup(volume, container=config.UNICODE_SYMBOLS)
    cli_cinder_steps.show_volume_backup(backup)


@pytest.mark.idempotent_id('ef21745a-6fdc-456b-8e2c-2533f24b5eae')
def test_volume_transfer_non_unicode_name(volume,
                                          transfer_steps,
                                          cli_cinder_steps,
                                          volume_steps):
    """**Scenario:** Create volume transfer with non unicode name.

    Note: transfer_steps fixture is used for transfer cleanup.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume transfer with non unicode name using CLI
    #. Check that volume status is 'awaiting-transfer'

    **Teardown:**

    #. Delete volume transfer
    #. Delete volume
    """
    cli_cinder_steps.create_volume_transfer(volume,
                                            name=config.UNICODE_SYMBOLS)
    volume_steps.check_volume_status(volume,
                                     status=config.STATUS_AWAITING_TRANSFER,
                                     timeout=config.VOLUME_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('0242150d-d187-46c0-94f8-36259989560d')
def test_create_volume_using_image_name(ubuntu_image,
                                        cli_cinder_steps,
                                        volume_steps):
    """**Scenario:** Create volume from image using image name.

    **Setup:**

    #. Create image

    **Steps:**

    #. Create volume from image using image name

    **Teardown:**

    #. Delete volume
    #. Delete image
    """
    volume_name = next(utils.generate_ids())
    cli_cinder_steps.create_volume(size=4, name=volume_name,
                                   image=ubuntu_image.name)
    volume = volume_steps.get_volumes(name_prefix=volume_name)[0]
    volume_steps.check_volume_status(
        volume,
        config.STATUS_AVAILABLE,
        transit_statuses=(config.STATUS_CREATING,
                          config.STATUS_DOWNLOADING,
                          config.STATUS_UPLOADING),
        timeout=config.VOLUME_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('c5ab08cf-6055-4940-9fff-f930bbcb1cbb')
def test_show_volume_transfer_non_unicode_name(volume,
                                               create_volume_transfer,
                                               cli_cinder_steps):
    """**Scenario:** Show volume transfer with non unicode name.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume transfer with non unicode name using API
    #. Check CLI command ``cinder transfer-show <transfer id>``

    **Teardown:**

    #. Delete volume transfer
    #. Delete volume
    """
    volume_transfer = create_volume_transfer(
        volume, transfer_name=config.UNICODE_SYMBOLS)
    cli_cinder_steps.show_volume_transfer(volume_transfer)
