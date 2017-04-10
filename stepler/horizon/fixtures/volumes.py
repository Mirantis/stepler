"""
--------------------
Fixtures for volumes
--------------------
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

from stepler.horizon import steps

__all__ = [
    'volumes_steps_ui',
]


@pytest.fixture
def volumes_steps_ui(volume_steps, snapshot_steps, backup_steps,
                     login, horizon):
    """Fixture to get volumes steps.

    volume_steps instance is used for volumes cleanup.
    snapshot_steps instance is used for snapshots cleanup.
    backup_steps instance is used for backups cleanup.

    Args:
        volume_steps (VolumeSteps): instantiated volume steps
        snapshot_steps (SnapshotSteps): instantiated snapshot steps
        backup_steps (BackupSteps): instantiated backup steps
        horizon (Horizon): instantiated horizon web application
        login (None): should log in horizon before steps using
    """
    return steps.VolumesSteps(horizon)
