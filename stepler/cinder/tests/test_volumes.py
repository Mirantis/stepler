"""
-----------
Volume tests
-----------
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

from stepler.third_party import utils


def test_create_volume(cinder_steps):
    """Verify that 10 cinder volumes can be created and deleted."""
    volumes_names = next(utils.generate_ids('volume', count=10))

    volume = cinder_steps.create_volumes(names=volumes_names)
    cinder_steps.delete_volume(volume)
