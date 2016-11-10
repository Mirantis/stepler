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
    'get_transfer_steps',
    'cleanup_transfers',
]


@pytest.fixture(scope='session')
def get_transfer_steps(get_cinder_client):
    """Callable session fixture to get volume transfer steps.

    Args:
        get_cinder_client (function): function to get cinder client.

    Returns:
        function: function to get transfer steps.
    """
    def _get_transfer_steps(**credentials):
        return steps.VolumeTransferSteps(
            get_cinder_client(**credentials).transfers)

    return _get_transfer_steps


@pytest.fixture
def transfer_steps(get_transfer_steps, cleanup_transfers):
    """Function fixture to get volume transfer steps.

    Args:
        get_transfer_steps (function): function to get transfer steps
        cleanup_transfers (function): function to cleanup transfers
            after test

    Yields:
        VolumeTransferSteps: instantiated transfer steps.
    """
    _transfer_steps = get_transfer_steps()
    transfers = _transfer_steps.get_transfers(all_projects=True, check=False)
    transfer_ids_before = {transfer.id for transfer in transfers}

    yield _transfer_steps
    cleanup_transfers(_transfer_steps, uncleanable_ids=transfer_ids_before)


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


@pytest.fixture
def cleanup_transfers(uncleanable):
    """Callable function fixture to clear created transfers after test.

    Args:
        uncleanable (AttrDict): data structure with skipped resources

    Returns:
        function: function to cleanup transfers
    """
    def _cleanup_transfers(_transfer_steps, uncleanable_ids=None):
        uncleanable_ids = uncleanable_ids or uncleanable.transfer_ids

        for transfer in _transfer_steps.get_transfers(all_projects=True,
                                                      check=False):
            if transfer.id not in uncleanable_ids:
                _transfer_steps.delete_volume_transfer(transfer)

    return _cleanup_transfers
