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
from stepler.third_party import utils

__all__ = [
    'get_snapshot_steps',
    'snapshot_steps',
    'cleanup_snapshots',
    'volume_snapshot',
]


@pytest.fixture(scope='session')
def get_snapshot_steps(get_cinder_client):
    """Callable session fixture to get snapshot steps.

    Args:
        get_cinder_client (function): function to get cinder client

    Returns:
        function: function to get snapshot steps
    """
    def _get_snapshot_steps(version, is_api, **credentials):
        return steps.SnapshotSteps(
            get_cinder_client(version, is_api, **credentials).volume_snapshots)

    return _get_snapshot_steps


@pytest.fixture
def snapshot_steps(get_snapshot_steps, cleanup_snapshots):
    """Function fixture to get snapshot steps.

    Args:
        cinder_client (object): instantiated cinder client
        cleanup_snapshots (function): function fixture to cleanup snapshots

    Yields:
         stepler.cinder.steps.SnapshotSteps: instantiated snapshot steps
    """
    _snapshot_steps = get_snapshot_steps(
        config.CURRENT_CINDER_VERSION, is_api=False)

    snapshots = _snapshot_steps.get_snapshots(check=False)
    snapshot_ids_before = {snapshot.id for snapshot in snapshots}

    yield _snapshot_steps
    cleanup_snapshots(_snapshot_steps, uncleanable_ids=snapshot_ids_before)


@pytest.fixture
def volume_snapshot(volume, snapshot_steps):
    """Function fixture to create snapshot with default options before test.

    Args:
        volume (object): cinder volume
        snapshot_steps (object): instantiated snapshot steps

    Returns:
        object: cinder volume snapshot
    """
    return snapshot_steps.create_snapshots(
        volume, names=utils.generate_ids())[0]


@pytest.fixture(scope='session')
def cleanup_snapshots(uncleanable):
    """Callable function fixture to cleanup snapshots after test.

    Args:
        uncleanable (AttrDict): data structure with skipped resources

    Returns:
        function: function to cleanup snapshots
    """
    def _cleanup_snapshots(_snapshot_steps, uncleanable_ids=None):
        uncleanable_ids = uncleanable_ids or uncleanable.snapshot_ids
        deleting_snapshots = []

        for snapshot in _snapshot_steps.get_snapshots(check=False):
            if snapshot.id not in uncleanable_ids:
                deleting_snapshots.append(snapshot)

        _snapshot_steps.delete_snapshots(deleting_snapshots)

    return _cleanup_snapshots
