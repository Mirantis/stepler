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


@pytest.mark.parametrize('disk_format', ['raw', 'qcow2'])
@pytest.mark.idempotent_id('7a8f8745-0348-458c-8cf6-143b4627276a')
def test_create_image_from_volume(upload_volume_to_image, disk_format):
    """**Scenario:** Verify that raw|qcow2 image is created from volume.
    
    **Steps:**
    
    #. Create cinder volume
    #. Create raw|qcow2 image from volume
    #. Delete raw|qcow2 image
    #. Delete cinder volume
    """
    volume_name = next(utils.generate_ids('volume'))
    image_name = next(utils.generate_ids('image'))

    upload_volume_to_image(volume_name, image_name, disk_format=disk_format)
