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

from stepler.third_party.utils import generate_ids


def test_create_volume(cinder_steps):
    """Verify that cinder image can be created and deleted."""
    volume_name = next(generate_ids('volume'))

    volume = cinder_steps.create_volume(name=volume_name)
    cinder_steps.delete_volume(volume)
