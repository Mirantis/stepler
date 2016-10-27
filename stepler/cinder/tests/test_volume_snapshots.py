"""
---------------
Snapshots tests
---------------
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


@pytest.mark.idempotent_id('0b2e09ad-ab3d-454d-9eb5-6dbdd1b1db52')
@pytest.mark.usefixtures('big_snapshot_quota')
def test_create_multiple_snapshots(volume, create_snapshots, snapshot_steps):
    """**Scenario:** Test creating multiple snapshots

    Note:
        This test verify bug #1452299

    **Setup:**

    #. Increase cinder snapshots count quota
    #. Create volume

    **Steps:**

    #. Create 70 snapshots from volume
    #. Delete created snapshots
    #. Create 50 snapshots from volume without waiting for creating
    #. Check that all 50 snapshots are created

    **Teardown:**

    #. Delete snapshots
    #. Delete volume
    #. Restore cinder snapshots count quota
    """
    names = utils.generate_ids('snapshot1', count=70)
    snapshots = create_snapshots(volume, names=names)
    snapshot_steps.delete_snapshots(snapshots)

    names = utils.generate_ids('snapshot1', count=50)
    snapshots = create_snapshots(volume, names=names, check=False)

    snapshot_steps.check_snapshots_status(
        snapshots,
        status=config.STATUS_AVAILABLE,
        timeout=len(snapshots) * config.SNAPSHOT_AVAILABLE_TIMEOUT)
