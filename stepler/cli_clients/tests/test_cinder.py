# -*- coding: utf-8 -*-
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


@pytest.mark.idempotent_id('225d218b-6562-431d-bdf9-0ec0221c0f86')
def test_volume_backup_non_unicode_name(volume, backups_cleanup,
                                        cli_cinder_steps, backup_steps):
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
    backup_dict = cli_cinder_steps.create_volume_backup(volume, name=u"シンダー")
    backup_steps.check_backup_status(backup_dict['id'],
                                     config.STATUS_AVAILABLE,
                                     timeout=config.BACKUP_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('07eb81c1-ca1f-4c65-93c4-f3378e62adfd')
def test_volume_backup_non_unicode_description(volume, backups_cleanup,
                                               cli_cinder_steps, backup_steps):
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
    backup_dict = cli_cinder_steps.create_volume_backup(volume,
                                                        description=u"シンダー")
    backup_steps.check_backup_status(backup_dict['id'],
                                     config.STATUS_AVAILABLE,
                                     timeout=config.BACKUP_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('107affa2-fc40-4c7e-8b11-cc1940bd7259')
def test_volume_snapshot_non_unicode_name(volume,
                                          snapshots_cleanup,
                                          cli_cinder_steps,
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
    snapshot_dict = cli_cinder_steps.create_volume_snapshot(volume,
                                                            name=u"シンダー")
    snapshot_steps.check_snapshots_status(
        [snapshot_dict['id']],
        config.STATUS_AVAILABLE,
        timeout=config.SNAPSHOT_AVAILABLE_TIMEOUT)


@pytest.mark.idempotent_id('98c66ba5-7932-45eb-86f9-9d76ae72851f')
def test_volume_snapshot_non_unicode_description(volume,
                                                 snapshots_cleanup,
                                                 cli_cinder_steps,
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
        volume, description=u"シンダー")
    snapshot_steps.check_snapshots_status(
        [snapshot_dict['id']],
        config.STATUS_AVAILABLE,
        timeout=config.SNAPSHOT_AVAILABLE_TIMEOUT)
