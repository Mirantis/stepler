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


@pytest.mark.idempotent_id('43b96116-a0ba-45cc-b584-af9ee838ba49')
def test_change_volume_type_from_empty(volume, volume_type, volume_steps):
    """**Scenario:** Verify change volume type from empty value.

    **Steps:**

    #. Create cinder volume without volume type
    #. Create new volume type
    #. Change volume type to newly created type

    **Teardown:**

    #. Delete volume
    #. Delete volume type
    """
    volume_steps.change_volume_type(volume, volume_type, config.POLICY_NEVER)


@pytest.mark.idempotent_id('a5cee93e-6d58-420e-a61c-85cbd10d6725')
def test_change_volume_type(create_volume_type, volume_steps):
    """**Scenario:** Verify change volume type.

    **Steps:**

    #. Create two volume types
    #. Create volume using first volume type
    #. Retype volume to another type

    **Teardown:**

    #. Delete volume
    #. Delete volume types
    """
    volume_type_1 = create_volume_type(next(utils.generate_ids()))
    volume_type_2 = create_volume_type(next(utils.generate_ids()))

    volume = volume_steps.create_volumes(volume_type=volume_type_1.name)[0]
    volume_steps.change_volume_type(volume, volume_type_2, config.POLICY_NEVER)
