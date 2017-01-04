"""
--------------
Keystone tests
--------------
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


@pytest.mark.idempotent_id('89ef26c6-600a-4f69-afeb-d3b8d9ad1244')
def test_keystone_permission_lose(admin,
                                  project,
                                  admin_role,
                                  project_steps,
                                  role_steps,
                                  user_steps):
    """**Scenario:** Check that admin have access to users and projects in this
    session.

    **Setup:**

    #. Create new project

    **Steps:**

    #. Add admin member with admin role to this project
    #. Remove the admin role for this project
    #. Check that admin is able to get projects and users

    **Teardown:**

    #. Delete project
    """
    role_steps.grant_role(admin_role, user=admin, project=project)
    role_steps.revoke_role(admin_role, user=admin, project=project)
    project_steps.get_projects()
    user_steps.get_users()


@pytest.mark.idempotent_id('76f823ac-5c8b-4617-a4cc-9e30257a679f')
def test_restart_keystone_service(cirros_image,
                                  tiny_flavor,
                                  keypair,
                                  net_subnet_router,
                                  security_group,
                                  server,
                                  get_ssh_proxy_cmd,
                                  user,
                                  create_user,
                                  user_steps,
                                  os_faults_steps,
                                  server_steps):
    """**Scenario:** Check that keystone works after restarting services.

    **Setup:**

    #. Create cirros image
    #. Create tiny flavor
    #. Create keypair
    #. Create network with subnet and router
    #. Create security group
    #. Create server_1
    #. Create user_1

    **Steps:**

    #. Check that ping from server_1 to 8.8.8.8 is successful
    #. Restart keystone services
    #. Check that user_1 is in user list
    #. Create server_2 and check ping to 8.8.8.8 and to server_1 as well
    #. Create user_2 and check its presence in user list

    **Teardown:**

    #. Delete users
    #. Delete servers
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete keypair
    #. Delete flavor
    #. Delete cirros image
    """
    proxy_cmd = get_ssh_proxy_cmd(server)
    with server_steps.get_server_ssh(
            server, proxy_cmd=proxy_cmd) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP, server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)

    os_faults_steps.restart_services([config.KEYSTONE])

    user_steps.check_user_presence(user)
    server_2 = server_steps.create_servers(image=cirros_image,
                                           flavor=tiny_flavor,
                                           networks=[net_subnet_router[0]],
                                           keypair=keypair,
                                           security_groups=[security_group],
                                           username=config.CIRROS_USERNAME)[0]
    proxy_cmd = get_ssh_proxy_cmd(server_2)
    server_1_ip = server_steps.get_fixed_ip(server)
    with server_steps.get_server_ssh(
            server_2, proxy_cmd=proxy_cmd) as server_ssh:
        server_steps.check_ping_for_ip(config.GOOGLE_DNS_IP, server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)
        server_steps.check_ping_for_ip(server_1_ip, server_ssh,
                                       timeout=config.PING_CALL_TIMEOUT)

    name_2, password_2 = utils.generate_ids(count=2)
    create_user(user_name=name_2, password=password_2)


@pytest.mark.idempotent_id('14ed4331-c05e-4b9a-9723-eac8c6f3f26a')
def test_check_objects_are_revoked(role_steps,
                                   get_project_steps,
                                   create_project,
                                   create_user):
    """**Scenario:** Check that keystone objects are revoked correctly.

    https://bugs.launchpad.net/mos/+bug/1546197
    When you delete a role assignment using a user+role+project pairing,
    unscoped tokens between the user+project are unnecessarily revoked as
    well. In fact, two events are created for each role assignment deletion
    (one that is scoped correctly and one that is scoped too broadly).

    **Setup:**

    #. Create project
    #. Create user

    **Steps:**

    #. Add new project in admin tenant
    #. Login under this user
    #. Get projects
    #. Delete new user from admin tenant
    #. Get projects

    **Teardown:**

    #. Delete user
    #. Delete project
    """
    user_name = next(utils.generate_ids('user'))
    user_password = next(utils.generate_ids('password'))
    project_name = next(utils.generate_ids('project'))

    project = create_project(project_name=project_name, domain='default')
    user = create_user(user_name,
                       user_password,
                       default_project=project)
    admin_role = role_steps.get_role(name='admin')
    role_steps.grant_role(role=admin_role, user=user, project=project)

    user_credentials = {'username': user_name,
                        'password': user_password,
                        'project_name': project_name}

    user_project_steps = get_project_steps(**user_credentials)
    user_project_steps.get_projects()
    role_steps.revoke_role(role=admin_role, user=user, project=project)
    user_project_steps.check_get_projects_requires_authentication()


@pytest.mark.idempotent_id('e52e771c-b8e4-4af5-981f-76b975e5b110')
def test_modify_project_members_update_quotas(admin_role,
                                              create_project,
                                              create_group,
                                              role_steps,
                                              project_steps):
    """**Scenario:** Failed to modify project members and update project quotas.

    https://bugs.launchpad.net/horizon/+bug/1326668

    **Setup:**

    #. Get admin role

    **Steps:**

    #. Create project
    #. Create group
    #. Add new project in admin tenant
    #. Get projects
    #. Delete new project from admin tenant
    #. Get projects

    **Teardown:**

    #. Delete group
    #. Delete project
    """
    project = create_project(next(utils.generate_ids('project')))
    group = create_group(next(utils.generate_ids('group')))

    role_steps.grant_role(role=admin_role, project=project, group=group)
    project_steps.get_projects()
    role_steps.revoke_role(role=admin_role, project=project, group=group)
    project_steps.get_projects()


@pytest.mark.idempotent_id('06bf8aba-9fa2-45e6-ac71-622fe0440541')
def test_user_list(user_steps):
    """**Scenario:** Request list of users.

    **Steps:**

    #. Get list of users
    """
    user_steps.get_users()


@pytest.mark.idempotent_id('9a306d49-a3ad-4632-bf5d-ef11b0a07995')
@pytest.mark.parametrize('new_user_with_project',
                         [{'with_role': True}], indirect=True)
def test_create_user_and_authenticate(new_user_with_project,
                                      get_server_steps):
    """**Scenario:** Create new user

    **Setup:**

    #. Create new user
    #. Create new project
    #. Create new user role
    #. Grant role to user for project

    **Steps:**

    #. Perform user authentication
    #. Get list of servers

    **Teardown:**

    #. Delete user role
    #. Delete project
    #. Delete user
    """
    server_steps = get_server_steps(**new_user_with_project)
    server_steps.get_servers(check=False)


services_list = [
    config.CEILOMETER,
    config.CINDER,
    config.CINDERV2,
    config.GLANCE,
    config.HEAT,
    config.HEAT_CNF,
    config.KEYSTONE,
    config.NEUTRON,
    config.NOVA,
    config.NOVA_EC2,
    config.NOVA20
]


@pytest.mark.idempotent_id('1304cc00-4797-48ee-9b36-fa2997ba96d6',
                           service_name=config.CEILOMETER)
@pytest.mark.idempotent_id('993d7997-43c9-4fa0-9bb2-82e138022574',
                           service_name=config.CINDER)
@pytest.mark.idempotent_id('2c48707f-863b-4849-8b3f-f39643abf23c',
                           service_name=config.CINDERV2)
@pytest.mark.idempotent_id('ebeea432-7045-4f95-bcf7-eceea9ab874a',
                           service_name=config.GLANCE)
@pytest.mark.idempotent_id('220a4390-64d1-49d1-8b39-a07b96cfa47f',
                           service_name=config.HEAT)
@pytest.mark.idempotent_id('6a0cc9ee-e102-4754-8adc-041ccad86a53',
                           service_name=config.HEAT_CNF)
@pytest.mark.idempotent_id('ee5acce0-ca90-43d5-9167-4df322bece79',
                           service_name=config.KEYSTONE)
@pytest.mark.idempotent_id('93d319d2-2faf-47df-8026-9bee641bf859',
                           service_name=config.NEUTRON)
@pytest.mark.idempotent_id('64ce7134-de41-48cd-a015-2e4c4f687e9f',
                           service_name=config.NOVA)
@pytest.mark.idempotent_id('ce7eed04-b057-4076-aac7-f5042b50b8e6',
                           service_name=config.NOVA_EC2)
@pytest.mark.idempotent_id('8274b37e-6dca-4fdc-9725-e07fdf185047',
                           service_name=config.NOVA20)
@pytest.mark.parametrize('service_name', services_list)
def test_service_list(service_steps, service_name):
    """**Scenario:** Create new user

    **Steps:**

    #. Get service by name and check if it exist
    """
    service_steps.get_service(service_name)
