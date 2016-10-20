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
import six

from cinderclient import exceptions

from stepler.third_party import utils


@pytest.mark.idempotent_id('965cb50a-2900-4788-974f-9def0648484a')
def test_create_delete_10_volumes(cinder_steps):
    """**Scenario:** Verify that 10 cinder volumes can be created and deleted.

    **Steps:**

    #. Create 10 cinder volumes
    #. Delete 10 cinder volumes
    """
    volumes_names = utils.generate_ids('volume', count=10)

    volumes = cinder_steps.create_volumes(names=volumes_names)
    cinder_steps.delete_volumes(volumes)


@pytest.mark.idempotent_id('45783965-096f-46d6-a863-e466cc9d2d49')
def test_create_volume_without_name(cinder_steps):
    """**Scenario:** Verify creation of volume without name

    **Steps:**

    #. Create volume without name
    """
    cinder_steps.create_volume()


@pytest.mark.idempotent_id('bcd12002-dfd3-44c9-b270-d844d61a009c')
def test_create_volume_long_name(cinder_steps):
    """**Scenario:** Verify creation of volume with name length > 255

    **Steps:**

    #. Create volume with name length > 255
    """
    long_name = utils.generate_ids(length=256)
    ex_text = "Name has more than 255 characters"

    six.assertRaisesRegex(exceptions.BadRequest, ex_text,
                          cinder_steps.create_volume,
                          name=long_name)


@pytest.mark.idempotent_id('8b08bc8f-e1f4-4f6e-8f98-dfcb1f9f538a')
def test_create_volume_description(cinder_steps):
    """**Scenario:** Verify creation of volume with description.

    **Steps:**

    #. Create volume with description
    """
    description = utils.generate_ids(prefix='volume')
    cinder_steps.create_volume(description=description)


@pytest.mark.idempotent_id('56cc7c76-ae92-423d-81ad-8cece5f875ad')
def test_create_volume_description_max(cinder_steps):
    """**Scenario:** Verify creation of volume with max description length.

    **Steps:**

    #. Create volume with description length == max(255)
    """
    description = utils.generate_ids(prefix='volume', length=255)
    cinder_steps.create_volume(description=description)
