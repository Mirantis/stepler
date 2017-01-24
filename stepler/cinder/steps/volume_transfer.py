"""
---------------------
Volume transfer steps
---------------------
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
from hamcrest import assert_that, calling, is_not, empty, equal_to, raises  # noqa

from stepler import base
from stepler import config
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ['VolumeTransferSteps']


class VolumeTransferSteps(base.BaseSteps):
    """Cinder volume transfer steps."""

    @steps_checker.step
    def get_transfers(self, search_opts=None, check=True):
        """Step to retrieve volume transfers.

        Args:
            search_opts (dict: optional): API filter options to
                retrieve transfers
            check (bool|True): flag whether to check step or not

        Returns:
            list: volume transfers list

        Raises:
            AssertionError: if check failed
        """
        transfers = self._client.list(search_opts=search_opts)

        if check:
            assert_that(transfers, is_not(empty()))
        return transfers

    @steps_checker.step
    def create_volume_transfer(self, volume, transfer_name, check=True):
        """Step to create volume transfer.

        Args:
            volume (obj): volume object
            transfer_name (str): name of created volume transfer
            check (bool|true): flag whether to check step or not

        Returns:
            object: cinder volume transfer

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        transfer = self._client.create(volume.id, name=transfer_name)

        if check:
            self.check_volume_transfer_presence(transfer, timeout=60)

        return transfer

    @steps_checker.step
    def check_volume_transfer_presence(self, transfer, must_present=True,
                                       timeout=0):
        """Check step volume transfer presence status.

        Args:
            transfer (object): cinder volume transfer to check presence status
            must_present (bool|True): flag whether volume type should present
            or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def _check_volume_transfer_presence():
            try:
                self._client.get(transfer.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_volume_transfer_presence, timeout_seconds=timeout)

    @steps_checker.step
    def delete_volume_transfer(self, transfer, check=True):
        """Step to delete(cancel) volume transfer.

        Args:
            transfer (obj): volume transfer object
            check (bool|true): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.delete(transfer.id)

        if check:
            self.check_volume_transfer_presence(
                transfer, must_present=False,
                timeout=config.VOLUME_AVAILABLE_TIMEOUT)

    @steps_checker.step
    def accept_volume_transfer(self, transfer, check=True):
        """Step to accept volume transfer.

        Args:
            transfer (obj): volume transfer object
            check (bool|true): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.accept(transfer.id, transfer.auth_key)

        if check:
            self.check_volume_transfer_presence(
                transfer, must_present=False,
                timeout=config.VOLUME_AVAILABLE_TIMEOUT)

    @steps_checker.step
    def check_transfer_not_created_with_long_transfer_name(self, volume,
                                                           transfer_name):
        """Step for negative test case of transfer creation with invalid name.

        Args:
            volume (obj): volume to create transfer
            transfer_name (str): name of transfer

        Raises:
            AssertionError: if check triggered an error
        """
        exception_message = "Transfer name has more than 255 characters"

        assert_that(
            calling(self.create_volume_transfer).with_args(
                volume, transfer_name, check=False),
            raises(exceptions.BadRequest, exception_message))
