"""
-----------------
Neutron CLI tests
-----------------
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


@pytest.mark.requires('dvr')
@pytest.mark.idempotent_id('3577df9a-5d1b-4cf5-b499-7cc907f2632e')
@pytest.mark.parametrize('distributed', [True, False])
def test_negative_create_distributed_router_with_member_user(
        cli_neutron_steps,
        new_user_with_project,
        router_steps,
        routers_cleanup,
        distributed):
    """**Scenario:** Check that DVR creation with explicit `distributed`
    option by user with member role is disallowed by policy.

    **Setup:**

    #. Create project
    #. Create user for project
    #. Grant member role to user

    **Steps:**

    #. Try to create router with parameter Distributed = True using CLI
    #. Try to create router with parameter Distributed = False using CLI
    #. Check that router creation is disallowed by policy

    **Teardown:**

    #. Delete router
    #. Delete user
    #. Delete project
    """
    router_name = next(utils.generate_ids())
    cli_neutron_steps.check_negative_router_create_with_distributed_option(
        router_name,
        project=new_user_with_project['project_name'],
        username=new_user_with_project['username'],
        password=new_user_with_project['password'],
        distributed=distributed)


@pytest.mark.requires('dvr')
@pytest.mark.idempotent_id('da31c8bf-19d2-4283-a976-52c704c8621f')
def test_create_distributed_router_with_member_user(
        cli_neutron_steps,
        new_user_with_project,
        router_steps,
        routers_cleanup):
    """**Scenario:** Create DVR without explicit `distributed`option
    by user with member role.

    **Setup:**

    #. Create project
    #. Create user for project
    #. Grant member role to user

    **Steps:**

    #. Create router without parameter Distributed using CLI
    #. Check that router parameter Distributed = True

    **Teardown:**

    #. Delete router
    #. Delete user
    #. Delete project
    """
    router_name = next(utils.generate_ids())
    cli_neutron_steps.create_router(
        router_name,
        project=new_user_with_project['project_name'],
        username=new_user_with_project['username'],
        password=new_user_with_project['password'])

    router_steps.check_router_attrs(router_name,
                                    expected_attr_values={'distributed': True})
