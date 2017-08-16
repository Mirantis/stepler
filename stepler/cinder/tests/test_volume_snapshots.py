"""
---------------
Snapshots tests
---------------
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

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('0b2e09ad-ab3d-454d-9eb5-6dbdd1b1db52')
@pytest.mark.usefixtures('big_snapshot_quota')
def test_create_multiple_snapshots(volume, snapshot_steps):
    """**Scenario:** Test creating multiple snapshots

    **Setup:**

    #. Increase cinder snapshots count quota
    #. Create volume

    **Steps:**

    #. Create 5 snapshots from volume
    #. Delete created snapshots without waiting for deleting
    #. Create 5 snapshots from volume without waiting for creating
    #. Delete 5 created snapshots without waiting for deleting
    #. Check that all 10 snapshots are deleted

    **Teardown:**

    #. Delete volume
    #. Restore cinder snapshots count quota
    """
    snapshot_number = 5
    names = utils.generate_ids(count=snapshot_number)
    snapshots = [snapshot_steps.create_snapshots(volume, names=[name])[0]
                 for name in names]
    snapshot_steps.delete_snapshots(snapshots, check=False)

    names = utils.generate_ids(count=snapshot_number)
    snapshots2 = snapshot_steps.create_snapshots(volume, names=names)
    snapshot_steps.delete_snapshots(snapshots2, check=False)

    snapshot_steps.check_snapshots_presence(
        snapshots + snapshots2, must_present=False,
        timeout=config.SNAPSHOT_DELETE_TIMEOUT)


@pytest.mark.idempotent_id('618cacba-0b25-41b1-9334-976b12e51652')
def test_snapshot_list(snapshot_steps):
    """**Scenario:** Request list of snapshots.

    **Steps:**

    #. Get list of snapshots
    """
    snapshot_steps.get_snapshots(check=False)
