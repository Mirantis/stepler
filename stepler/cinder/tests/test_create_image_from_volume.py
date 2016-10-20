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
from stepler.third_party.utils import generate_ids  # noqa


@pytest.yield_fixture
def upload_volume_to_image(create_volume, cinder_steps, glance_steps):
    """Function fixture to upload volume to image.

    Can be called several times during a test.
    After the test it destroys all created objects.

    Args:
        create_volume (function): function to create volume with options
        cinder_steps (function): function to get cinder steps
        glance_steps (function): function to get glance steps

    Returns:
        object: glance image
    """
    images = []

    def _upload_volume_to_image(volume_name, image_name, disk_format):
        volume = create_volume(volume_name)
        image_info = cinder_steps.volume_upload_to_image(
            volume=volume, image_name=image_name, disk_format=disk_format)
        image = glance_steps.get_image(
            image_info['os-volume_upload_image']['image_id'])
        images.append(image)
        glance_steps.check_image_status(image, status='active',
                                        timeout=config.IMAGE_AVAILABLE_TIMEOUT)
        return image

    yield _upload_volume_to_image

    glance_steps.delete_images(images)


@pytest.mark.idempotent_id('f5259a1b-8b4a-4057-897d-e8d8efe0ab6b')
def test_create_raw_image_from_volume(upload_volume_to_image):
    """**Scenario:** Verify that raw image can be created from volume.

    **Steps:**

    #. Create cinder volume
    #. Create raw image from volume
    #. Delete cinder volume
    #. Delete raw image
    """
    volume_name = next(generate_ids('volume'))
    image_name = next(generate_ids('image'))

    upload_volume_to_image(volume_name, image_name, disk_format='raw')


@pytest.mark.idempotent_id('7a8f8745-0348-458c-8cf6-143b4627276a')
def test_create_qcow2_image_from_volume(upload_volume_to_image):
    """**Scenario:** Verify that qcow2 image can be created from volume.

    **Steps:**

    #. Create cinder volume
    #. Create qcow2 image from volume
    #. Delete cinder volume
    #. Delete qcow2 image
    """
    volume_name = next(generate_ids('volume'))
    image_name = next(generate_ids('image'))

    upload_volume_to_image(volume_name, image_name, disk_format='qcow2')
