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
from stepler import config
from stepler.third_party import context
from stepler.third_party import utils

__all__ = [
    'snapshot_steps',
    'snapshots_cleanup',
    'volume_snapshot',
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
def volume_snapshot(volume, snapshot_steps):
    """Function fixture to create snapshot with default options before test.

    Args:
        volume (object): cinder volume
        snapshot_steps (object): instantiated snapshot steps

    Returns:
        object: cinder volume snapshot
    """
    snapshot_name = next(utils.generate_ids('snapshot'))
    return snapshot_steps.create_snapshots(volume, snapshot_name)[0]


@pytest.fixture
def snapshots_cleanup(uncleanable):
    """Callable function fixture to cleanup snapshots after test.

    Args:
        uncleanable (AttrDict): data structure with skipped resources

    Returns:
        function: function to cleanup snapshots
    """
    @context.context
    def _snapshots_cleanup(snapshot_steps):

        def _get_snapshots():
            return snapshot_steps.get_snapshots(
                name_prefix=config.STEPLER_PREFIX,
                check=False)

        snapshots_ids_before = [snapshot.id for snapshot in _get_snapshots()]

        yield

        deleting_snapshots = []
        for snapshot in _get_snapshots():
            if ((snapshot.id not in uncleanable.snapshot_ids) and
                    (snapshot.id not in snapshots_ids_before)):
                deleting_snapshots.append(snapshot)

        snapshot_steps.delete_snapshots(deleting_snapshots)

    return _snapshots_cleanup
