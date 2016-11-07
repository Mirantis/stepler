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


@pytest.mark.parametrize('size', [-1, 1])
@pytest.mark.idempotent_id('adcb5b96-35a3-401b-8ca2-3bc13ee225b9')
def test_negative_extend_volume(volume_steps, size):
    """**Scenario:** Verify negative cases of volume extend.

    **Steps:**

    #. Create cinder volume
    #. Try to extend volume to negative/smaller size
    #. Check that volume extending was not performed

    **Teardown:**

    #. Delete cinder volume

    """
    volume = volume_steps.create_volumes(size=2)[0]
    volume_steps.check_volume_extend_failed_incorrect_size(volume, size)


@pytest.mark.idempotent_id('50baaa82-82de-4698-96fc-aa58f91f3ee2')
def test_positive_extend_volume(volume, create_volume, volume_steps):
    """**Scenario:** Verify nominal volume extend.

    **Steps:**

    #. Create cinder volume
    #. Extend volume to correct size
    #. Check that volume extending was performed

    **Teardown:**

    #. Delete cinder volume

    """
    volume_steps.volume_extend(volume, size=2)


@pytest.mark.idempotent_id('0cdc2fd5-eb07-4930-b004-077d16200091')
def test_negative_extend_volume_more_than_limit(session,
                                                volume,
                                                cinder_quota_steps,
                                                project_steps,
                                                volume_steps):
    """**Scenario:** Verify negative cases of volume extend (size > limit).

    **Steps:**

    #. Create cinder volume
    #. Try to extend volume to size which is more than quota
    #. Check that volume extending was not performed

    **Teardown:**

    #. Delete cinder volume

    """
    current_project = project_steps.get_current_project(session)
    size = cinder_quota_steps.get_volume_size_quota(current_project) + 1
    volume_steps.check_volume_extend_failed_size_more_than_limit(volume, size)
