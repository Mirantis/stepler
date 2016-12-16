"""
--------------
Security tests
--------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('46e8a669-1204-4427-a2e3-bbe21a87333d')
@pytest.mark.requires('glance_swift')
def test_change_glance_credentials(request, cirros_image, glance_steps):
    """**Scenario:** Check image available after changing glance credentials.

    **Setup:**

    #. Create cirros image

    **Steps:**

    #. Change glance credentials on keystone and glance_api.conf
    #. Download cirros image
    #. Delete cirros image

    **Teardown:**

    #. Restore glance credentials
    #. Delete cirros image
    """
    request.getfixturevalue('change_glance_credentials')
    glance_steps.check_image_content(
        cirros_image, utils.get_file_path(config.CIRROS_QCOW2_URL))
