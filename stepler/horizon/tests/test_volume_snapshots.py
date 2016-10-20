"""
---------------------
Volume snapshot tests
---------------------
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

import pytest

from stepler.horizon.utils import generate_ids


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for any user."""

    def test_edit_volume_snapshot(self, snapshot, volumes_steps):
        """Verify that user can edit volume snapshot."""
        new_snapshot_name = snapshot.name + '(updated)'
        with snapshot.put(name=new_snapshot_name):
            volumes_steps.update_snapshot(snapshot.name, new_snapshot_name)

    def test_volume_snapshots_pagination(self, volumes_steps, create_snapshots,
                                         update_settings):
        """Verify that snapshots pagination works right and back."""
        snapshot_names = list(generate_ids(prefix='snapshot', count=3))
        create_snapshots(snapshot_names)
        update_settings(items_per_page=1)
        volumes_steps.check_snapshots_pagination(snapshot_names)

    def test_create_volume_from_snapshot(self, snapshot, volumes_steps):
        """Verify that user cat create volume from snapshot."""
        volumes_steps.create_volume_from_snapshot(snapshot.name)
        volumes_steps.delete_volume(snapshot.name)
