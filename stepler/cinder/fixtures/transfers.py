"""
------------------------
Volume transfer fixtures
------------------------
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
    'transfer_steps',
    'create_volume_transfer',
]


@pytest.fixture
def transfer_steps(cinder_client):
    """Function fixture to get volume transfer steps.

    Args:
        cinder_client (object): instantiated cinder client

    Returns:
        stepler.cinder.steps.VolumeTransferSteps: instantiated transfer steps
    """
    return steps.VolumeTransferSteps(cinder_client.transfers)


@pytest.yield_fixture
def create_volume_transfer(transfer_steps):
    """Callable function fixture to create volume transfer with options.

    Can be called several times during test.

    Args:
        transfer_steps (VolumeTransferSteps): instantiated transfer steps

    Yields:
        function: function to create singe volume transfer with options
    """
    volume_transfers = []

    def _create_volume_transfer(*args, **kwgs):
        volume_transfer = transfer_steps.create_volume_transfer(*args, **kwgs)
        volume_transfers.append(volume_transfer)
        return volume_transfer

    yield _create_volume_transfer

    for volume_transfer in volume_transfers:
        transfer_steps.delete_volume_transfer(volume_transfer)
