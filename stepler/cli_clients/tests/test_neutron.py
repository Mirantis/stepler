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

from stepler import config
from stepler.third_party import utils


@pytest.mark.requires('dvr')
@pytest.mark.idempotent_id('3577df9a-5d1b-4cf5-b499-7cc907f2632e')
def test_create_distributed_router_with_member_user(
        cli_neutron_steps,
        current_project,
        create_user,
        role_steps,
        router_steps,
        routers_cleanup):
    """**Scenario:** Create DVR by user with member role.

    **Steps:**

    #. Create user for admin tenant
    #. Assign user member role
    #. Try to create router with parameter Distributed = True using CLI
    #. Try to create router with parameter Distributed = False using CLI
    #. Create router without parameter Distributed using CLI
    #. Check that router parameter Distributed = True

    **Teardown:**

    #. Delete router
    #. Delete user
    """
    user_name = next(utils.generate_ids())
    user = create_user(user_name=user_name,
                       password=user_name,
                       default_project=current_project)
    member_role = role_steps.get_role(name=config.ROLE_MEMBER)
    role_steps.grant_role(member_role, user=user,
                          project=current_project)

    router_name = next(utils.generate_ids())
    cli_neutron_steps.check_negative_router_create_with_distributed_option(
        router_name,
        project=current_project.name,
        username=user_name,
        password=user_name,
        distributed=True)
    cli_neutron_steps.check_negative_router_create_with_distributed_option(
        router_name,
        project=current_project.name,
        username=user_name,
        password=user_name,
        distributed=False)
    cli_neutron_steps.create_router(router_name,
                                    project=current_project.name,
                                    username=user_name,
                                    password=user_name)

    router_steps.check_router_attrs(router_name,
                                    expected_attr_values={'distributed': True})
