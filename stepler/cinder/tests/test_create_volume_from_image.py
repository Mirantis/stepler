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


@pytest.mark.parametrize("disk_format", ["raw", "qcow2"])
@pytest.mark.idempotent_id('daf829d8-9b81-47f3-9a34-2fe5e9bdfa3a')
def test_create_volume_from_image(create_image, create_volume, disk_format):
    """**Scenario:** Verify that volume from raw|qcow2 image is created.

    **Steps:**

    #. Create cinder volume from raw|qcow2 image
    #. Delete cinder volume
    """
    image_name = next(utils.generate_ids('image'))
    image = create_image(image_name,
                         config.UBUNTU_ISO_URL,
                         disk_format=disk_format)
    volume_name = next(utils.generate_ids('volume'))
    create_volume(volume_name, image=image)
