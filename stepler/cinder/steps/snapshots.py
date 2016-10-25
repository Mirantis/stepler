"""
--------------
Snapshot steps
--------------
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

from cinderclient import exceptions
from hamcrest import assert_that, equal_to, has_entries, is_not, empty  # noqa
import waiting

from stepler import base
from stepler import config
from stepler.third_party import steps_checker

__all__ = ['SnapshotSteps']


class SnapshotSteps(base.BaseSteps):
    """Snapshot steps."""

    @steps_checker.step
    def create_snapshot(self, volume, name=None, check=True):
        """Step to create volume.

        Args:
            volume (object): volume of the snapshot

        Return:
            snapshot (object): cinder snapshot

        Raises:
            TimeoutExpired|AssertionError: if check was falsed
        """

        snapshot = self._client.volume_snapshots.create(name=name,
                                                        volume_id=volume.id)
        if check:
            self.check_snapshot_status(snapshot, 'available',
                                       timeout=config
                                       .SNAPSHOT_AVAILABLE_TIMEOUT)
            assert_that(snapshot.volume_id, equal_to(volume.id))

        return snapshot

    @steps_checker.step
    def delete_snapshot(self, snapshot, check=True):
        """Step to delete snapshot.

        Args:
            snapshot (object): cinder volume snapshot
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        self._client.volume_snapshots.delete(snapshot=snapshot.id)
        if check:
            self.check_snapshot_presence(snapshot,
                                         present=False,
                                         timeout=config
                                         .SNAPSHOT_DELETE_TIMEOUT)

    @steps_checker.step
    def check_snapshot_presence(self, snapshot, present=True, timeout=0):
        """Check step snapshot presence status.
        Args:
            snapshot (object): cinder volume snapshot to check presence status
            presented (bool): flag whether snapshot should present or no
            timeout (int): seconds to wait a result of check
        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            try:
                self._client.volume_snapshots.get(snapshot.id)
                return present
            except exceptions.NotFound:
                return not present

        waiting.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def check_snapshot_status(self, snapshot, status, timeout=0):
        """Check step snapshot status.
        Args:
            snapshot (object): cinder volume snapshot to check status
            status (str): snapshot status name to check
            timeout (int): seconds to wait a result of check
        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            snapshot.get()
            return snapshot.status.lower() == status.lower()

        waiting.wait(predicate, timeout_seconds=timeout)
