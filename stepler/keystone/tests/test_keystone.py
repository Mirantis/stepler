"""
--------------
Keystone tests
--------------

@author: schipiga@mirantis.com
"""

#    Copyright 2016 Mirantis, Inc.
#
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


@pytest.mark.testrail_id('851868')
def test_keystone_permission_lose(admin, project, admin_role, project_steps,
                                  role_steps, user_steps):
    """Check that admin have access to users and projects in this session.

    Scenario:
    1. Login as admin
    2. Create a new project
    3. Add admin member with admin role to this new project
    4. Remove the admin role for this project
    5. Check that admin is able to get projects and users
    """
    role_steps.grant_role(admin_role, user=admin, project=project)
    role_steps.revoke_role(admin_role, user=admin, project=project)
    project_steps.get_projects()
    user_steps.get_users()


@pytest.mark.testrail_id('1295474')
@pytest.mark.check_env_('is_ha')
def test_restart_all_services(cirros_image, keypair, security_group,
                              create_user, create_server,
                              user_steps, flavor_steps, neutron_steps,
                              server_steps):
    """Check that keystone works after restarting all keystone services

    Scenario:
    1. Create new user
    2. Check 'test_user1' present in user list
    3. Restart apache2 services on all computes
    4. Create new user 'test_user2'
    5. Check 'test_user2' present in user list
    6. Check 'test_user1' present in user list
    7. Create VM
    8. Check reach ACTIVE status
    """

    user1 = create_user(user_name='test_user1', password='test_user1')
    user_steps.check_user_presence(user1)

    # TODO(ssokolov) apache restart is not yet implemented
    # # Restart keystone services
    # for node in env.get_nodes_by_role('controller'):
    #     with node.ssh() as remote:
    #         remote.check_call('service apache2 restart')
    #
    user2 = create_user(user_name='test_user2', password='test_user2')
    user_steps.check_user_presence(user2)
    user_steps.check_user_presence(user1)

    # TODO(ssokolov) it would be great to add default values for parameters of
    # create_server (as much as possible), ex: cirros_image etc.
    # Ideally, this test should call it without params
    flavor = flavor_steps.find(name='m1.tiny')
    network = neutron_steps.find(name='admin_internal_net')
    server = create_server(server_name="server_1295474",
                           image=cirros_image,
                           flavor=flavor,
                           network=network,
                           keypair=keypair,
                           security_groups=[security_group])
    server_steps.check_server_status(server, 'active')
