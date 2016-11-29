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


@pytest.mark.idempotent_id('7a8f8745-0348-458c-8cf6-143b4627276a',
                           disk_format='raw')
@pytest.mark.idempotent_id('c74f8a82-7905-4215-b604-f902a6228a70',
                           disk_format='qcow2')
@pytest.mark.idempotent_id('d3f83a8c-eafc-4cd0-b72c-dfb56fce5cea',
                           disk_format='vdi')
@pytest.mark.idempotent_id('4a1f2935-6128-424a-aa7a-d9532ab6668b',
                           disk_format='vmdk')
@pytest.mark.parametrize('disk_format', ['raw', 'qcow2', 'vdi', 'vmdk'])
def test_create_image_from_volume(upload_volume_to_image, disk_format):
    """**Scenario:** raw/qcow2/vdi/vmdk image is created from volume.

    **Steps:**

    #. Create cinder volume
    #. Create image from volume
    #. Delete image
    #. Delete cinder volume
    """
    upload_volume_to_image(disk_format=disk_format)
