# coding=utf-8
"""
------------
Volume tests
------------
"""

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('521e09ac-034b-461c-aa0d-9242f06b7f7d')
def test_negative_create_volume_transfer_long_name(volume, transfer_steps):
    """**Scenario:** Verify creation of volume transfer with name length > 255.

    **Setup:**

        #. Create cinder volume

    **Steps:**

        #. Try to create volume transfer with name length > 255
        #. Check that BadRequest exception raised

    **Teardown:**
        #. Delete cinder volume
    """
    long_name = next(utils.generate_ids(length=256))
    transfer_steps.check_negative_transfer_not_created(volume,
                                                       transfer_name=long_name)


@pytest.mark.idempotent_id('a2441208-2c59-4bd0-a2bf-97663ad59084')
@pytest.mark.parametrize('transfer_name', ["シンダ", None])
def test_create_volume_transfer(volume, create_volume_transfer, transfer_name):
    """**Scenario:** Verify creation of volume transfer.

    **Setup:**

        #. Create cinder volume

    **Steps:**

        #. Create volume transfer with non-unicode name

    **Teardown:**

        #. Delete volume transfer
        #. Delete cinder volume
    """
    create_volume_transfer(volume, transfer_name)


@pytest.mark.idempotent_id('20118b84-0114-4cc5-a461-5fb5148303b2')
def test_create_and_accept_volume_transfer(volume, volume_steps,
                                           transfer_steps):
    """**Scenario:** Verify create and accept of volume transfer.

    **Setup:**

        #. Create cinder volume

    **Steps:**

        #. Create volume transfer
        #. Accept volume transfer

    **Teardown:**

        #. Delete cinder volume
    """
    transfer_name = next(utils.generate_ids("transfer"))
    transfer = transfer_steps.create_volume_transfer(volume, transfer_name)
    volume_steps.check_volume_status(volume, config.STATUS_AWAITING_TRANSFER,
                                     timeout=config.VOLUME_AVAILABLE_TIMEOUT)
    transfer_steps.accept_volume_transfer(transfer)
    volume_steps.check_volume_status(volume, config.STATUS_AVAILABLE,
                                     timeout=config.VOLUME_AVAILABLE_TIMEOUT)
