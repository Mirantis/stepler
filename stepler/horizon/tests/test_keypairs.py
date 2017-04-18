"""
-------------
Keypair tests
-------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import pytest

from stepler.third_party import utils


with open(os.path.join(os.path.dirname(__file__), 'test_data',
                       'key.pub')) as f:
    PUBLIC_KEY = f.read()


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any user."""

    @pytest.mark.idempotent_id('57b7621f-174c-4373-8d6c-bbd6991172ff',
                               any_one='admin')
    @pytest.mark.idempotent_id('4e1445fd-c820-4d6b-a9a8-f95a764d7ec4',
                               any_one='user')
    def test_create_keypair(self, keypairs_steps_ui):
        """**Scenario:** Verify that user can create keypair.

        **Steps:**

        #. Create keypair using UI
        #. Delete keypair using UI
        """
        keypair_name = keypairs_steps_ui.create_keypair()
        keypairs_steps_ui.delete_keypair(keypair_name)

    @pytest.mark.idempotent_id('b5701a3c-1ee2-4a0e-9d19-c03f160424ca',
                               any_one='admin')
    @pytest.mark.idempotent_id('5475edda-e404-4887-afe0-ef3d249de09c',
                               any_one='user')
    def test_import_keypair(self, keypairs_steps_ui):
        """**Scenario:** Verify that user can import keypair.

        **Steps:**

        #. Import keypair using UI

        **Teardown:**

        #. Delete keypair using API
        """
        keypair_name = next(utils.generate_ids('keypair'))
        keypairs_steps_ui.import_keypair(keypair_name, PUBLIC_KEY)
