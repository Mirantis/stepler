"""
-----------
Volume tests
-----------
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

from stepler.third_party.utils import generate_ids, get_file_path  # noqa


@pytest.mark.idempotent_id('daf829d8-9b81-47f3-9a34-2fe5e9bdfa3a')
def test_create_volume_from_qcow2_image(create_volume,
                                        ubuntu_qcow2_image_for_cinder):
    """**Scenario:** Verify that cinder volumes
    from qcow2 image can be created.

    **Steps:**

    #. Create cinder volume from qcow2 image
    #. Delete cinder volume
    """
    volume_name = next(generate_ids('volume'))
    create_volume(volume_name, image=ubuntu_qcow2_image_for_cinder)


@pytest.mark.idempotent_id('d00aeda9-d9b3-425d-befb-512f3ff8bfb6')
def test_create_volume_from_raw_image(create_volume,
                                      ubuntu_raw_image_for_cinder):
    """**Scenario:** Verify that cinder volumes
    from raw import image can be created.

    **Steps:**

    #. Create cinder volume from raw image
    #. Delete cinder volume
    """
    volume_name = next(generate_ids('volume'))
    create_volume(volume_name, image=ubuntu_raw_image_for_cinder)
