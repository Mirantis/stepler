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

from stepler.third_party import utils


@pytest.mark.usefixtures('any_one')
class TestAnyOne(object):
    """Tests for anyone."""

    @pytest.mark.idempotent_id('53c038f0-b63c-461c-983b-7db82fd0d626',
                               any_one='admin', instances_count=2)
    @pytest.mark.idempotent_id('ecb6230a-3062-46af-af06-4f9208ae2961',
                               any_one='admin', instances_count=1)
    @pytest.mark.idempotent_id('acf99c3a-c22c-4e33-a58e-58a49d94877f',
                               any_one='user', instances_count=2)
    @pytest.mark.idempotent_id('bf0ea67b-fe0a-4be3-bc83-e9ca8ba0b3e2',
                               any_one='user', instances_count=1)
    @pytest.mark.parametrize('instances_count', [2, 1])
    def test_delete_instances(self, instances_count, create_instance):
        """Verify that user can delete instances as batch."""
        instance_name = utils.generate_ids('instance').next()
        create_instance(instance_name, count=instances_count)

    @pytest.mark.idempotent_id('005870b0-73fd-4c56-a6ec-8c4bad46f058',
                               any_one='admin')
    @pytest.mark.idempotent_id('e534aeb2-b0d4-407c-9f89-64a5c0739513',
                               any_one='user')
    def test_lock_instance(self, instance, instances_steps):
        """Verify that user can lock instance."""
        instances_steps.lock_instance(instance.name)
        instances_steps.unlock_instance(instance.name)

    @pytest.mark.idempotent_id('6a01661b-c7af-47ad-9aaa-8b185dda8d3c',
                               any_one='admin')
    @pytest.mark.idempotent_id('48649a7b-6496-4ff9-9041-dcb52f1324f3',
                               any_one='user')
    def test_view_instance(self, instance, instances_steps):
        """Verify that user can view instance details."""
        instances_steps.view_instance(instance.name)

    @pytest.mark.idempotent_id('8867776e-ff19-49a7-8d10-ea78cc02cfc6',
                               any_one='admin')
    @pytest.mark.idempotent_id('de45feb0-85bb-4b54-b8dc-0ead39620bfa',
                               any_one='user')
    def test_instances_pagination(self, instances_steps, create_instance,
                                  update_settings):
        """Verify that instances pagination works right and back."""
        instance_name = next(utils.generate_ids('instance'))
        instances = create_instance(instance_name, count=3)
        update_settings(items_per_page=1)
        instances_steps.check_instances_pagination(instances)

    @pytest.mark.idempotent_id('060136f-d477-4177-a387-8e8d01ec4ecd',
                               any_one='admin')
    @pytest.mark.idempotent_id('edc5f03d-ea66-4dae-8322-7cd679c2d829',
                               any_one='user')
    def test_filter_instances(self, instances_steps, create_instance):
        """Verify that user can filter instances."""
        instance_name = next(utils.generate_ids('instance'))
        instances = create_instance(instance_name, count=2)

        instances_steps.filter_instances(query=instances[0].name)
        instances_steps.reset_instances_filter()
