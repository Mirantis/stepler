"""
-----------------------------
Cinder volume snapshots steps
-----------------------------
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

from cinderclient import exceptions
from hamcrest import assert_that, equal_to, is_not, empty
import waiting

from stepler import base
from stepler import config
from stepler.third_party import steps_checker

__all__ = ['VolumeSnapshotSteps']


class VolumeSnapshotSteps(base.BaseSteps):
    """Cinder volume snapshots steps."""

    @steps_checker.step
    def create(self, name, volume, check=True):
        """Step to create volume snapshot.

        Args:
            name (str): name of snapshot
            volume (obj): cinder colume to create snapshot from
            check (bool|True): flag whether to check step or not

        Returns:
            obj: created snapshot

        Raises:
            AssertionError: if check was falsed
        """
        snapshot = self._client.create(volume.id, name=name)
        if check:
            self.check_status(
                snapshot,
                status=config.STATUS_AVAILABLE,
                transit_statuses=(config.STATUS_CREATING, ),
                timeout=config.SNAPSHOT_AVAILABLE_TIMEOUT)
        return snapshot

    @steps_checker.step
    def delete(self, snapshot, check=True):
        """Step to delete volume snapshot.

        Args:
            snapshot (obj): snapshot object to delete
            check (bool|True): flag whether to check step or not

        Raises:
            AssertionError: if check was falsed
        """
        snapshot.delete()
        if check:
            self.check_presence(
                snapshot,
                present=False,
                timeout=config.SNAPSHOT_DELETE_TIMEOUT)

    @steps_checker.step
    def get_snapshots(self, check=True):
        """Step to get all volumes' snapshots.

        Args:
            check (bool|True): flag whether to check step or not

        Returns:
            list: list of all snapshots

        Raises:
            AssertionError: if check was falsed
        """
        snapshots = list(self._client.list())
        if check:
            assert_that(snapshots, is_not(empty()))
        return snapshots

    @steps_checker.step
    def check_status(self, snapshot, status, transit_statuses=(), timeout=0):
        """Verify step to check snapshot status.

        Args:
            snapshot (obj): snapshot to check status
            status (str): expected snapshot status
            transit_statuses (iterable): allowed transit statuses
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            snapshot.get()
            return snapshot.status.lower() not in transit_statuses

        waiting.wait(predicate, timeout_seconds=timeout)
        assert_that(snapshot.status.lower(), equal_to(status.lower()))

    @steps_checker.step
    def check_presence(self, snapshot, present=True, timeout=0):
        """Check-step to check snapshot presence.

        Args:
            snapshot (obj): snapshot to check presence
            present (bool): flag to check is snapshot present or absent
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            try:
                self._client.get(timeout.id)
                return present
            except exceptions.NotFound:
                return not present

        waiting.wait(predicate, timeout_seconds=timeout)
