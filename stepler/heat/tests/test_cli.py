"""
----------------
Heat stack tests
----------------
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


@pytest.mark.idempotent_id('ed10d63a-a155-415a-9df4-4d653af00181')
def test_stack_create_from_file(nova_api_node, create_stack_cli,
                                get_template_path, os_faults_steps):
    """**Scenario:** Create stack from template file with CLI.

    **Setup:**

        #. Upload template to node

    **Steps:**

        #. Create stack from template
        #. Check that stack is exists

    **Teardown:**

        #. Delete stack
    """
    template_path = get_template_path('empty_heat_template')
    remote_path = os_faults_steps.upload_file(nova_api_node, template_path)
    parameters = {'param': 'string'}
    stack_name = next(utils.generate_ids('stack'))
    create_stack_cli(
        nova_api_node,
        stack_name,
        template_file=remote_path,
        parameters=parameters)


@pytest.mark.idempotent_id('60d6d01b-5e52-42c5-951d-ff487ba14cd4')
def test_stack_create_from_url(nova_api_node, create_stack_cli):
    """**Scenario:** Create stack from template url with CLI.

    **Steps:**

        #. Create stack from template
        #. Check that stack is exists

    **Teardown:**

        #. Delete stack
    """
    stack_name = next(utils.generate_ids('stack'))
    create_stack_cli(
        nova_api_node,
        stack_name,
        template_url=config.HEAT_SIMPLE_TEMPLATE_URL)
