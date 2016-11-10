"""
--------------
Snapshot steps
--------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from hamcrest import assert_that, equal_to, has_entries, is_not, empty  # noqa

from stepler import base
from stepler import config
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ['SnapshotSteps']


class SnapshotSteps(base.BaseSteps):
    """Snapshot steps."""

    @steps_checker.step
    def create_snapshots(self,
                         volume,
                         names,
                         check=True):
        """Step to create snapshots.

        Args:
            volume (object): volume of the snapshots
            names (str): name of created snapshots
            check (bool): flag whether to check step or not

        Returns:
            list: cinder volume snapshots

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        snapshots = []
        for name in names:
            snapshot = self._client.create(name=name, volume_id=volume.id)
            snapshots.append(snapshot)

        if check:
            self.check_snapshots_status(
                snapshots,
                config.STATUS_AVAILABLE,
                timeout=config.SNAPSHOT_AVAILABLE_TIMEOUT)
            for snapshot in snapshots:
                assert_that(snapshot.volume_id, equal_to(volume.id))

        return snapshots

    @steps_checker.step
    def delete_snapshots(self, snapshots, check=True):
        """Step to delete snapshots.

        Args:
            snapshots (list): cinder volume snapshots
            check (bool): flag whether to check step or not

        Raises:
           TimeoutExpired: if check failed after timeout
        """
        for snapshot in snapshots:
            self._client.delete(snapshot=snapshot.id)

        if check:
            self.check_snapshots_presence(
                snapshots,
                must_present=False,
                timeout=len(snapshots) * config.SNAPSHOT_DELETE_TIMEOUT)

    @steps_checker.step
    def check_snapshots_presence(self,
                                 snapshots,
                                 must_present=True,
                                 timeout=0):
        """Step to check snapshots presence status.

        Args:
            snapshots (list): cinder volume snapshots to check presence status
            must_present (bool): flag whether snapshot should present
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        snapshot_ids = [snapshot.id for snapshot in snapshots]
        # Make a dict with desired presence values for each snapshot
        expected_presence = dict.fromkeys(snapshot_ids, must_present)

        def _check_snapshots_presence():
            # Make a dict with actual presence values for each snapshot
            actual_presence = dict.fromkeys(snapshot_ids, False)
            for snapshot in self._client.list():
                if snapshot.id in actual_presence:
                    actual_presence[snapshot.id] = True
            return expect_that(actual_presence, equal_to(expected_presence))

        waiter.wait(_check_snapshots_presence, timeout_seconds=timeout)

    @steps_checker.step
    def check_snapshots_status(self, snapshots, status, timeout=0):
        """Step to check snapshots status.

        Args:
            snapshots (list): list of cinder volume snapshot objects
                or their ids to check status
            status (str): snapshot status name to check
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        for snapshot in snapshots:
            if not hasattr(snapshot, 'id'):
                snapshot = self.get_snapshot_by_id(snapshot)

            def _check_snapshots_status():
                snapshot.get()
                return expect_that(snapshot.status.lower(),
                                   equal_to(status.lower()))

            waiter.wait(_check_snapshots_status, timeout_seconds=timeout)

    @steps_checker.step
    def get_snapshots(self, name_prefix=None, check=True):
        """Step to get snapshots.

        Args:
            name_prefix (str): name prefix to filter snapshots
            check (bool): flag whether to check step or not

        Returns:
            list: snapshots collection

        Raises:
            AssertionError: if check failed
        """
        snapshots = list(self._client.list())

        if name_prefix:
            snapshots = [snapshot for snapshot in snapshots
                         if (snapshot.name or '').startswith(name_prefix)]

        if check:
            assert_that(snapshots, is_not(empty()))
        return snapshots

    @steps_checker.step
    def get_snapshot_by_id(self, snapshot_id, check=True):
        """Step to get snapshot object from cinder using snapshot id.

        Args:
            snapshot_id (str): volume snapshot id
            check (bool): flag whether to check step or not

        Returns:
            object: volume snapshot

        Raises:
            NotFound: if snapshot with snapshot_id doesn't exist
            AssertionError: if check failed
        """
        snapshot = self._client.get(snapshot_id)

        if check:
            assert_that(snapshot.id, equal_to(snapshot_id))

        return snapshot
