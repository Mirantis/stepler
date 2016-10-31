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

__all__ = [
    'backup_steps',
    'create_backup',
]


@pytest.fixture
def backup_steps(cinder_client):
    """Function fixture to get volume backup steps.

    Args:
        cinder_client (object): instantiated cinder client

    Returns:
        stepler.cinder.steps.BackupSteps: instantiated backup steps
    """
    return steps.BackupSteps(cinder_client.backups)


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
