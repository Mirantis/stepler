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

from stepler import base
from stepler import config
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ['SnapshotSteps']


class SnapshotSteps(base.BaseSteps):
    """Snapshot steps."""

    @steps_checker.step
    def create_snapshot(self,
                        volume,
                        name=None,
                        check=True):
        """Step to create snapshot.

        Args:
            volume (object): volume of the snapshot
            name (str): name of created snapshot
            check (bool): flag whether to check step or not

        Return:
            snapshot (object): cinder snapshot

        Raises:
            TimeoutExpired|AssertionError: if check was falsed
        """

        snapshot = self._client.create(name=name,
                                       volume_id=volume.id)
        if check:
            self.check_snapshot_status(snapshot,
                                       config.STATUS_AVAILABLE,
                                       timeout=config.
                                       SNAPSHOT_AVAILABLE_TIMEOUT)
            assert_that(snapshot.volume_id, equal_to(volume.id))

        return snapshot

    @steps_checker.step
    def create_snapshots(self,
                         volume,
                         names,
                         check=True):
        """Step to create volumes.

        Args:
            volume (object): volume of the snapshots
            names (str): name of created snapshots
            check (bool): flag whether to check step or not

        Returns:
            list: cinder volume snapshots

        Raises:
            TimeoutExpired|AssertionError: if check was falsed
        """
        snapshots = []
        for name in names:
            snapshot = self.create_snapshot(volume=volume,
                                            name=name,
                                            check=False)
            snapshots.append(snapshot)

        if check:
            for snapshot in snapshots:
                self.check_snapshot_status(snapshot, config.STATUS_AVAILABLE,
                                           timeout=config
                                           .SNAPSHOT_AVAILABLE_TIMEOUT)
                assert_that(snapshot.volume_id, equal_to(volume.id))

        return snapshots

    @steps_checker.step
    def delete_snapshot(self, snapshot, check=True):
        """Step to delete snapshot.

        Args:
            snapshot (object): cinder volume snapshot
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        self._client.delete(snapshot=snapshot.id)
        if check:
            self.check_snapshots_presence(snapshot,
                                          must_present=False,
                                          timeout=config
                                          .SNAPSHOT_DELETE_TIMEOUT)

    @steps_checker.step
    def delete_snapshots(self, snapshots, check=True):
        """Step to delete snapshots.

        Args:
            snapshots (list): cinder volume snapshots
            check (bool): flag whether to check step or not

        Raises:
           TimeoutExpired: if check was falsed after timeout
        """
        for snapshot in snapshots:
            self.delete_snapshot(snapshot, check=False)

        if check:
            self.check_snapshots_presence(snapshots,
                                          must_present=False,
                                          timeout=config
                                          .SNAPSHOT_DELETE_TIMEOUT)

    @steps_checker.step
    def check_snapshots_presence(self,
                                 snapshots,
                                 must_present=True,
                                 timeout=0):
        """Check step snapshots presence status.

        Args:
            snapshots (list): cinder volume snapshots to check presence status
            presented (bool): flag whether snapshot should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        for snapshot in snapshots:
            def predicate():
                try:
                    self._client.get(snapshot.id)
                    is_present = True
                except exceptions.NotFound:
                    is_present = False
                return expect_that(is_present, equal_to(must_present))

        waiter.wait(predicate, timeout_seconds=timeout)

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
            return expect_that(snapshot.status.lower(),
                               equal_to(status.lower()))

        waiter.wait(predicate, timeout_seconds=timeout)
