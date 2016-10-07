"""
--------------
Instance tests
--------------
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
    """Tests for anyone."""

    @pytest.mark.parametrize('instances_count', [2, 1])
    def test_delete_instances(self, instances_count, create_instance):
        """Verify that user can delete instances as batch."""
        instance_name = generate_ids('instance').next()
        create_instance(instance_name, count=instances_count)

    def test_lock_instance(self, instance, instances_steps):
        """Verify that user can lock instance."""
        instances_steps.lock_instance(instance.name)
        instances_steps.unlock_instance(instance.name)

    def test_view_instance(self, instance, instances_steps):
        """Verify that user can view instance details."""
        instances_steps.view_instance(instance.name)

    def test_instances_pagination(self, instances_steps, create_instance,
                                  update_settings):
        """Verify that instances pagination works right and back."""
        instance_name = next(generate_ids('instance'))
        create_instance(instance_name, count=3)
        update_settings(items_per_page=1)
        # TODO(schipiga): move it to check step
        # page_instances = instances_steps.page_instances()
        # page_instances.table_instances.row(
        #     name=instances[2].name).wait_for_presence(30)
        # page_instances.table_instances.link_next.wait_for_presence()
        # page_instances.table_instances.link_prev.wait_for_absence()

        # page_instances.table_instances.link_next.click()

        # page_instances.table_instances.row(
        #     name=instances[1].name).wait_for_presence(30)
        # page_instances.table_instances.link_next.wait_for_presence()
        # page_instances.table_instances.link_prev.wait_for_presence()

        # page_instances.table_instances.link_next.click()

        # page_instances.table_instances.row(
        #     name=instances[0].name).wait_for_presence(30)
        # page_instances.table_instances.link_next.wait_for_absence()
        # page_instances.table_instances.link_prev.wait_for_presence()

        # page_instances.table_instances.link_prev.click()

        # page_instances.table_instances.row(
        #     name=instances[1].name).wait_for_presence(30)
        # page_instances.table_instances.link_next.wait_for_presence()
        # page_instances.table_instances.link_prev.wait_for_presence()

        # page_instances.table_instances.link_prev.click()

        # page_instances.table_instances.row(
        #     name=instances[2].name).wait_for_presence(30)
        # page_instances.table_instances.link_next.wait_for_presence()
        # page_instances.table_instances.link_prev.wait_for_absence()

    def test_filter_instances(self, instances_steps, create_instance):
        """Verify that user can filter instances."""
        instance_name = next(generate_ids('instance'))
        instances = create_instance(instance_name, count=2)

        instances_steps.filter_instances(query=instances[0].name)
        instances_steps.reset_instances_filter()
