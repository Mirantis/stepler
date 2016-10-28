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
    transfer_steps.check_transfer_not_created_with_long_tranfer_name(volume, 
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
