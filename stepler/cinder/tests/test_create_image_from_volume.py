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

from stepler.third_party.utils import generate_ids  # noqa


@pytest.mark.idempotent_id('f5259a1b-8b4a-4057-897d-e8d8efe0ab6b')
def test_create_raw_image_from_volume(cinder_steps, glance_steps):
    """**Scenario:** Verify that raw image can be created from volume.

    **Steps:**

    #. Create cinder volume
    #. Create raw image from volume
    #. Delete cinder volume
    #. Delete raw image
    """
    volume_name = next(generate_ids('volume'))
    image_name = next(generate_ids('image'))

    volume = cinder_steps.create_volume(volume_name)
    image = cinder_steps.volume_upload_to_image(volume=volume,
                                                image_name=image_name)

    glance_image = glance_steps.get_image(
        image['os-volume_upload_image']['image_id'])
    glance_steps.delete_image(glance_image)


@pytest.mark.idempotent_id('7a8f8745-0348-458c-8cf6-143b4627276a')
def test_create_qcow2_image_from_volume(cinder_steps, glance_steps):
    """**Scenario:** Verify that qcow2 image can be created from volume.

    **Steps:**

    #. Create cinder volume
    #. Create qcow2 image from volume
    #. Delete cinder volume
    #. Delete qcow2 image
    """
    volume_name = next(generate_ids('volume'))
    image_name = next(generate_ids('image'))

    volume = cinder_steps.create_volume(volume_name)
    image = cinder_steps.volume_upload_to_image(volume=volume,
                                                image_name=image_name,
                                                disk_format='qcow2')

    glance_image = glance_steps.get_image(
        image['os-volume_upload_image']['image_id'])
    glance_steps.delete_image(glance_image)
