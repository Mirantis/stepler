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
from stepler.cinder.steps import VolumeTransferSteps

__all__ = [
    'transfer_steps',
    'create_volume_transfer',
    'get_transfer_steps',
]


@pytest.fixture()
def get_transfer_steps(get_cinder_client):
    """Callable session fixture to get server steps.

    Args:
        get_nova_client (function): function to get nova client.

    Returns:
        function: function to get server steps.
    """
    def _get_transfer_steps(*args, **kwargs):
        return VolumeTransferSteps(get_cinder_client(*args, **kwargs).transfers)

    return _get_transfer_steps


# @pytest.fixture
# def transfer_steps(cinder_client):
#     """Function fixture to get volume transfer steps.
#
#     Args:
#         cinder_client (object): instantiated cinder client
#
#     Returns:
#         stepler.cinder.steps.VolumeTransferSteps: instantiated transfer steps
#     """
#     return steps.VolumeTransferSteps(cinder_client.transfers)


@pytest.fixture
def transfer_steps(get_transfer_steps):
    """Function fixture to get nova steps.

    Args:
        get_server_steps (function): function to get server steps
        servers_cleanup (function): function to make servers cleanup right
            after server steps initialization

    Returns:
        ServerSteps: instantiated server steps.
    """
    _server_steps = get_transfer_steps()
    return _server_steps


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
