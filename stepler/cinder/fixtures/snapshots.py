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


@pytest.fixture
def snapshot(volume, snapshot_steps):
    """Function fixture to create snapshot with default options before test.

    Args:
        volume (object):  cinder volume
        snapshot_steps (object): instantiated snapshot steps

    Returns:
        object: cinder volume snapshot
    """
    snapshot_name = next(utils.generate_ids('snapshot'))
    return snapshot_steps.create_snapshots(volume, snapshot_name)
