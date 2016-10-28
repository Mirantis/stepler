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
