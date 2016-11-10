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
from stepler.third_party import context

__all__ = [
    'get_backup_steps',
    'backup_steps',
    'create_backup',
    'backups_cleanup',
]


@pytest.fixture(scope='session')
def get_backup_steps(get_cinder_client):
    """Callable session fixture to get volume backup steps.

    Args:
        get_cinder_client (object): function to get cinder client

    Returns:
        function: function to get backup steps
    """
    def _get_backup_steps(**credentials):
        return steps.BackupSteps(get_cinder_client(**credentials).backups)

    return _get_backup_steps


@pytest.fixture
def backup_steps(get_backup_steps, backups_cleanup):
    """Function fixture to get volume backup steps.

    Args:
        get_backup_steps (object): function to get backup steps

    Yields:
        stepler.cinder.steps.BackupSteps: instantiated backup steps
    """
    _backup_steps = get_backup_steps()
    with backups_cleanup(_backup_steps):
        yield _backup_steps


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


@pytest.fixture
def backups_cleanup(uncleanable):
    """Callable function fixture to clear created backups after test.

    It stores ids of all backups before test and remove all new backups
    after test.

    Args:
        uncleanable (AttrDict): data structure with skipped resources

    Returns:
        function: function to cleanup backups
    """
    @context.context
    def _backups_cleanup(backup_steps):
        def _get_backups():
            return backup_steps.get_backups(prefix=config.STEPLER_PREFIX,
                                            check=False)

        backups_ids_before = set(backup.id for backup in _get_backups())

        yield

        for backup in _get_backups():
            if (backup.id not in uncleanable.backup_ids and
                    backup.id not in backups_ids_before):
                backup_steps.delete_backup(backup)

    return _backups_cleanup
