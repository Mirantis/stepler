"""
-----------------
Snapshot fixtures
-----------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #    http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# # implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.

import pytest

from stepler.cinder import steps
from stepler.third_party import utils

__all__ = [
    'snapshot_steps',
    'create_snapshot',
    'volume_snapshot',
]


@pytest.fixture
def snapshot_steps(cinder_client):
    """Function fixture to get snapshot steps.

    Args:
        cinder_client (object): instantiated cinder client

     Returns:
         stepler.cinder.steps.SnapshotSteps: instantiated snapshot steps
    """
    return steps.SnapshotSteps(cinder_client)


@pytest.yield_fixture
def create_snapshot(snapshot_steps):
    """Callable function fixture to create volumes with options.
    Can be called several times during a test.
    After the test it destroys all created volumes.
    Args:
        volume_steps (object): instantiated volume steps
    Returns:
        function: function to create volumes as batch with options
    """
    snapshots = []

    def _create_snapshot(volume, name=None, *args, **kwgs):
        _snapshot = snapshot_steps.create_snapshot(volume, name, *args, **kwgs)
        snapshots.append(_snapshot)
        return _snapshot

    yield _create_snapshot

    for snapshot in snapshots:
        snapshot_steps.delete_snapshot(snapshot)


@pytest.yield_fixture
def volume_snapshot(volume, create_snapshot):
    snapshot_name = next(utils.generate_ids('snapshot'))
    return create_snapshot(volume, name=snapshot_name)
