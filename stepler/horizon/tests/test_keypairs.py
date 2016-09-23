"""
Keypair tests.

@author: schipiga@mirantis.com
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

from os import path

import pytest

with open(path.join(path.dirname(__file__), 'test_data', 'key.pub')) as f:
    PUBLIC_KEY = f.read()


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any user."""

    def test_create_keypair(self, keypair):
        """Verify that user can create keypair."""

    def test_import_keypair(self, import_keypair):
        """Verify that user cat import keypair."""
        import_keypair(PUBLIC_KEY)
