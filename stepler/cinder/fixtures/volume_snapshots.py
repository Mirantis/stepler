"""
--------------------------------
Cinder volume snapshots fixtures
--------------------------------
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

__all__ = [
    'volume_snapshots_steps',
    'create_volume_snapshot',
]


@pytest.fixture
def volume_snapshots_steps(cinder_client):
    """Function fixture to get cinder volume snapshot steps.

    Args:
        cinder_client (object): instantiated cinder client

    Returns:
        stepler.cinder.steps.VolumeSnapshotSteps: instantiated volume snapshot
        steps
    """
    return steps.VolumeSnapshotSteps(cinder_client.volume_snapshots)


@pytest.yield_fixture
def create_volume_snapshot(volume_snapshots_steps):
    """Callable function fixture to create single volume snapshot with options.

    Can be called several times during a test.
    After the test it destroys all created volumes' snapshots.

    Args:
        volume_snapshots_steps (obj): instantiated volume snapshot steps

    Returns:
        function: function to create single volume snapshot with options
    """
    names = set()

    def _create_volume_snapshot(name, *args, **kwargs):
        names.add(name)
        snapshot = volume_snapshots_steps.create(name, *args, **kwargs)
        return snapshot

    yield _create_volume_snapshot

    if names:
        for snapshot in volume_snapshots_steps.get_snapshots(check=False):
            if snapshot.name in names:
                volume_snapshots_steps.delete(snapshot)
