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


@pytest.mark.idempotent_id('2df43a46-72b0-4d25-bf68-13d07776af7c')
@pytest.mark.parametrize('new_volume_name',
                         ['', next(utils.generate_ids('volume'))])
def test_edit_volume_name(volume_steps, new_volume_name):
    """**Scenario:** Verify ability to change volume name.

    **Steps:**

    #. Create volume
    #. Change volume name

    **Teardown:**

    #. Delete volume
    """
    volume = volume_steps.create_volumes(names=[None])[0]
    volume_steps.update_volume(volume, new_name=new_volume_name)


@pytest.mark.idempotent_id('1c5ef0e5-64ac-43d5-b9f2-97cb4ad62e95')
@pytest.mark.parametrize('new_volume_description',
                         ['', next(utils.generate_ids('description'))])
def test_edit_volume_description(volume_steps, new_volume_description):
    """**Scenario:** Verify ability to change volume description.

    **Steps:**

    #. Create volume
    #. Change volume description

    **Teardown:**

    #. Delete volume
    """
    volume = volume_steps.create_volumes(names=[None])[0]
    volume_steps.update_volume(volume, new_description=new_volume_description)


@pytest.mark.idempotent_id('f9561bef-2455-4274-8926-c2d6670752e1')
def test_negative_edit_volume_name_too_long_name(volume_steps):
    """**Scenario:** Verify inability to change volume name to name >255 chars.

    **Steps:**

    #. Create volume
    #. Try to change volume name to name longer than 255 characters

    **Teardown:**

    #. Delete volume
    """
    volume = volume_steps.create_volumes(names=[None])[0]
    volume_new_name = next(utils.generate_ids(length=256))
    volume_steps.check_volume_update_failed(volume, new_name=volume_new_name)


@pytest.mark.idempotent_id('7cb4af1e-2228-43ca-bc78-719d85fb0b2a')
def test_volume_enable_bootable(volume_steps):
    """**Scenario:** Verify ability to enable volume bootable status.

    **Steps:**

    #. Create volume
    #. Enable volume bootable status

    **Teardown:**

    #. Delete volume
    """
    volume = volume_steps.create_volumes(names=[None])[0]
    volume_steps.set_volume_bootable(volume, True)


@pytest.mark.idempotent_id('515ff471-e814-4074-8026-680a2131942c')
def test_volume_disable_bootable(glance_steps, volume_steps):
    """**Scenario:** Verify ability to disable volume bootable status.

    **Steps:**

    #. Create image
    #. Create volume from image
    #. Disable volume bootable status

    **Teardown:**

    #. Delete volume
    #. Delete image
    """
    image = glance_steps.create_images(
        utils.generate_ids('image'),
        utils.get_file_path(config.UBUNTU_ISO_URL))[0]

    volume = volume_steps.create_volumes(names=[None], image=image)[0]
    volume_steps.set_volume_bootable(volume, False)
