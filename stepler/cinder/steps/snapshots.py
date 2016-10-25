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
            TimeoutExpired|AssertionError: if check was falsed
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
    def delete_snapshots(self, snapshots, must_present=True, check=True):
        """Step to delete snapshots.

        Args:
            snapshots (list): cinder volume snapshots
            must_present (bool): flag whether snapshot should present
            check (bool): flag whether to check step or not

        Raises:
           TimeoutExpired: if check was falsed after timeout
        """
        for snapshot in snapshots:
            self._client.delete(snapshot=snapshot.id)

        if check:
            self.check_snapshots_presence(
                snapshots,
                must_present=False,
                timeout=config.SNAPSHOT_DELETE_TIMEOUT)

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
    def check_snapshots_status(self, snapshots, status, timeout=0):
        """Step to check snapshot status.

        Args:
            snapshots (object): cinder volume snapshots to check status
            status (str): snapshot status name to check
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        for snapshot in snapshots:

            def predicate():
                snapshot.get()
                return expect_that(snapshot.status.lower(),
                                   equal_to(status.lower()))

            waiter.wait(predicate, timeout_seconds=timeout)
