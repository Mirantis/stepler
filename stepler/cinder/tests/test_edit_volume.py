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


def test_edit_volume_name(create_volume, volume_steps):
    """**Scenario:** Verify ability to change volume name

    **Steps:**

        #. Create volume
        #. Change volume name

    **Teardown:**

        #. Delete volume
    """
    volume = create_volume()
    volume_new_name = next(utils.generate_ids(prefix='volume'))
    volume_steps.update_volume(volume, new_name=volume_new_name)


def test_edit_volume_description(create_volume, volume_steps):
    """**Scenario:** Verify ability to change volume description

    **Steps:**

        #. Create volume
        #. Change volume description

    **Teardown:**

        #. Delete volume
    """
    volume = create_volume()
    volume_new_description = next(utils.generate_ids('description'))
    volume_steps.update_volume(volume, new_description=volume_new_description)


def test_negative_edit_volume_name_too_long_name(create_volume, volume_steps):
    """**Scenario:** Verify inability to change volume name to name longer
    than 255 symbols

    **Steps:**

        #. Create volume
        #. Try to change volume name to name longer than 255 characters

    **Teardown:**

        #. Delete volume
    """
    volume = create_volume()
    volume_new_name = next(utils.generate_ids(length=256))
    volume_steps.check_volume_update_failed(volume, new_name=volume_new_name)


@pytest.mark.idempotent_id('7cb4af1e-2228-43ca-bc78-719d85fb0b2a')
def test_volume_enable_bootable(create_volume, volume_steps):
    """**Scenario:** Verify ability to enable volume bootable status

    **Steps:**

        #. Create volume
        #. Enable volume bootable status

    **Teardown:**

        #. Delete volume
    """
    volume = create_volume()
    volume_steps.set_volume_bootable(volume, True)


@pytest.mark.idempotent_id('515ff471-e814-4074-8026-680a2131942c')
def test_volume_disable_bootable(create_image, create_volume, volume_steps):
    """**Scenario:** Verify ability to disable volume bootable status

    **Steps:**

        #. Create image
        #. Create volume from image
        #. Disable volume bootable status

    **Teardown:**

        #. Delete volume
        #. Delete image
    """
    image_name = next(utils.generate_ids('image'))
    image = create_image(image_name, config.UBUNTU_ISO_URL)
    volume = create_volume(image=image)
    volume_steps.set_volume_bootable(volume, False)
