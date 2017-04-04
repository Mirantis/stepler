"""
---------------
Backup fixtures
---------------
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

__all__ = [
    'get_backup_steps',
    'backup_steps',
    'create_backup',
    'cleanup_backups',
]


@pytest.fixture(scope='session')
def get_backup_steps(get_cinder_client):
    """Callable session fixture to get volume backup steps.

    Args:
        get_cinder_client (object): function to get cinder client

    Returns:
        function: function to get backup steps
    """
    def _get_backup_steps(version, is_api, **credentials):
        return steps.BackupSteps(
            get_cinder_client(version, is_api, **credentials).backups)

    return _get_backup_steps


@pytest.fixture
def backup_steps(get_backup_steps, cleanup_backups):
    """Function fixture to get volume backup steps.

    Args:
        get_backup_steps (object): function to get backup steps
        cleanup_backups (function): function to cleanup backups after test

    Yields:
        stepler.cinder.steps.BackupSteps: instantiated backup steps
    """
    _backup_steps = get_backup_steps(
        config.CURRENT_CINDER_VERSION, is_api=False)

    backups = _backup_steps.get_backups(check=False)
    backup_ids_before = {backup.id for backup in backups}

    yield _backup_steps
    cleanup_backups(_backup_steps, uncleanable_ids=backup_ids_before)


@pytest.yield_fixture
def create_backup(backup_steps):
    """Callable function fixture to create single volume backup with options.

    Can be called several times during a test.
    After the test it destroys all created backups.

    Args:
        backup_steps (object): instantiated volume backup steps

    Returns:
        function: function to create volume backup as batch with options
    """
    backups = []

    def _create_backup(*args, **kwgs):
        _backup = backup_steps.create_backup(*args, **kwgs)
        backups.append(_backup)
        return _backup

    yield _create_backup

    for backup in backups:
        backup_steps.delete_backup(backup)


@pytest.fixture(scope='session')
def cleanup_backups(uncleanable):
    """Callable function fixture to clear created backups after test.

    It stores ids of all backups before test and remove all new backups
    after test.

    Args:
        uncleanable (AttrDict): data structure with skipped resources

    Returns:
        function: function to cleanup backups
    """
    def _cleanup_backups(_backup_steps, uncleanable_ids=None):
        uncleanable_ids = uncleanable_ids or uncleanable.backup_ids

        for backup in _backup_steps.get_backups(check=False):
            if backup.id not in uncleanable_ids:
                _backup_steps.delete_backup(backup)

    return _cleanup_backups
