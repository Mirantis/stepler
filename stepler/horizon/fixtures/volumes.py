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

from stepler import config
from stepler.horizon import steps
from stepler.third_party import utils

__all__ = [
    'create_backups',
    'create_snapshot',
    'create_snapshots',
    'snapshot',
    'volumes_steps_ui',
]


@pytest.fixture
def volumes_steps_ui(login, horizon):
    """Fixture to get volumes steps."""
    return steps.VolumesSteps(horizon)


@pytest.fixture
def snapshot(create_snapshot):
    """Fixture to create volume snapshot with default options before test."""
    snapshot_name = next(utils.generate_ids('snapshot'))
    return create_snapshot(snapshot_name)


@pytest.yield_fixture
def create_snapshots(volume, volumes_steps_ui):
    """Callable fixture to create volume snapshots with options.

    Can be called several times during test.
    """
    snapshots = []

    def _create_snapshots(snapshot_names):
        _snapshots = []

        for snapshot_name in snapshot_names:
            volumes_steps_ui.create_snapshot(volume.name, snapshot_name,
                                             check=False)
            volumes_steps_ui.close_notification('info')
            snapshot = utils.AttrDict(name=snapshot_name)

            snapshots.append(snapshot)
            _snapshots.append(snapshot)

        tab_snapshots = volumes_steps_ui._tab_snapshots()
        for snapshot_name in snapshot_names:
            tab_snapshots.table_snapshots.row(
                name=snapshot_name).wait_for_status('Available',
                                                    config.EVENT_TIMEOUT)

        return _snapshots

    yield _create_snapshots

    if snapshots:
        volumes_steps_ui.delete_snapshots(
            [snapshot.name for snapshot in snapshots])


@pytest.yield_fixture
def create_snapshot(volume, volumes_steps_ui):
    """Callable fixture to create snapshot with options.

    Can be called several times during test.
    """
    snapshots = []

    def _create_snapshot(snapshot_name, *args, **kwargs):
        volumes_steps_ui.create_snapshot(volume.name, snapshot_name, *args,
                                         **kwargs)
        snapshot = utils.AttrDict(name=snapshot_name)
        snapshots.append(snapshot)
        return snapshot

    yield _create_snapshot

    for snapshot in snapshots:
        volumes_steps_ui.delete_snapshot(snapshot.name)


@pytest.yield_fixture
def create_backups(volume, volumes_steps_ui):
    """Callable fixture to create backups with options.

    Can be called several times during test.
    """
    backups = []

    def _create_backups(backup_names, *args, **kwargs):
        _backups = []

        for backup_name in backup_names:
            volumes_steps_ui.create_backup(volume.name, backup_name, *args,
                                           **kwargs)
            backup = utils.AttrDict(name=backup_name)

            backups.append(backup)
            _backups.append(backup)

        return _backups

    yield _create_backups

    if backups:
        volumes_steps_ui.delete_backups([b.name for b in backups])
