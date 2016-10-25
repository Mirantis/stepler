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
    'create_snapshots',
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
    return steps.SnapshotSteps(cinder_client.volume_snapshots)


@pytest.yield_fixture
def create_snapshots(snapshot_steps):
    """Callable function fixture to create snapshots with options.

    Can be called several times during a test.
    After the test it destroys all created snapshots.

    Args:
        snapshot_steps (object): instantiated snapshot steps

    Returns:
        function: function to create snapshots as batch with options
    """
    snapshots = []

    def _create_snapshots(volume, names, *args, **kwgs):
        _snapshots = snapshot_steps.create_snapshots(
            volume, names, *args, **kwgs)
        snapshots.extend(_snapshots)
        return _snapshots

    yield _create_snapshots

    snapshot_steps.delete_snapshots(snapshots)


@pytest.yield_fixture
def create_snapshot(create_snapshots):
    """Callable function fixture to create volumes with options.

    Can be called several times during a test.
    After the test it destroys all created volumes.

    Args:
        snapshot_steps (object): instantiated snapshot steps

    Returns:
        function: function to create volumes as batch with options
    """
    def _create_snapshot(volume, name=None, *args, **kwgs):
        return create_snapshots(volume, [name], *args, **kwgs)[0]

    return _create_snapshot


@pytest.yield_fixture
def volume_snapshot(volume, create_snapshot):
    """Function fixture to create snapshot with default options before test.

    Args:
        volume (object):  cinder volume
        create_snapshot (function): function to create single snapshot

    Returns:
        object: cinder volume snapshot
    """
    snapshot_name = next(utils.generate_ids('snapshot'))
    return create_snapshot(volume, snapshot_name)
