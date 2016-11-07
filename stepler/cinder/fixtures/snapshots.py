"""
-----------------
Snapshot fixtures
-----------------
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

from stepler.cinder import steps
from stepler.third_party import utils

__all__ = [
    'snapshot_steps',
    'snapshot',
    'snapshots_cleanup',
]


@pytest.fixture
def snapshot_steps(cinder_client, snapshots_cleanup):
    """Function fixture to get snapshot steps.

    Args:
        cinder_client (object): instantiated cinder client
        snapshots_cleanup (function): function fixture to cleanup snapshots

    Yields:
         stepler.cinder.steps.SnapshotSteps: instantiated snapshot steps
    """
    _snapshot_steps = steps.SnapshotSteps(cinder_client.volume_snapshots)

    with snapshots_cleanup(_snapshot_steps):
        yield _snapshot_steps


@pytest.fixture
def snapshot(volume, snapshot_steps):
    """Function fixture to create snapshot with default options before test.

    Args:
        volume (object): cinder volume
        snapshot_steps (object): instantiated snapshot steps

    Returns:
        object: cinder volume snapshot
    """
    snapshot_name = next(utils.generate_ids('snapshot'))
    return snapshot_steps.create_snapshot(volume, snapshot_name)


@pytest.fixture
def snapshots_cleanup(snapshot_steps):
    """Function fixture to clear created snapshots after test.
    It stores ids of all snapshots before test and remove all new
    snapshots after test.
    Args:
        snapshot_steps (object): instantiated volume snapshot steps
    """
    preserve_snapshot_ids = set(
        snapshot.id for snapshot in snapshot_steps.get_snapshots(check=False))

    yield

    deleting_snapshots = []
    for snapshot in snapshot_steps.get_snapshots(check=False):
        if snapshot.id not in preserve_snapshot_ids:
            deleting_snapshots.append(snapshot)

    snapshot_steps.delete_snapshots(deleting_snapshots)
