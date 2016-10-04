"""
--------------
Keystone tests
--------------

@author: ssokolov@mirantis.com
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


AUTH_DATA = {
    'openldap1': ('user01', '1111'),
    'openldap2': ('user1', '1111'),
    'AD2': ('user01', 'qwerty123!')
}
LDAP_DOMAIN_NAMES = AUTH_DATA.keys()
LDAP_DOMAIN_GROUPS = {
    'AD2': 'Administrators',
    'openldap2': 'group01'
}

# @pytest.mark.undestructive
# @pytest.mark.testrail_id('1295439', with_proxy=True)
# @pytest.mark.testrail_id('1681468', with_proxy=False)
# @pytest.mark.ldap
# @pytest.mark.check_env_("is_ldap_plugin_installed")
# @pytest.mark.parametrize('with_proxy', [True, False])
# def test_ldap_basic_functions(os_conn, env, with_proxy):
def test_ldap_basic_functions(domain_steps, group_steps, user_steps):
    """Test to cover basic functionality

    Steps:
    1. Find LDAP domains
    2. For each domain, checks lists of users and groups
    """

    # if with_proxy != conftest.is_ldap_proxy(env):
    #     enabled_or_disabled = 'enabled' if with_proxy else 'disabled'
    #     pytest.skip("LDAP proxy is not {}".format(enabled_or_disabled))
    #
    for domain_name in LDAP_DOMAIN_NAMES:
        domain = domain_steps.find_domain(name=domain_name)
        group_steps.get_groups(domain=domain)
        user_steps.get_users(domain=domain)


# @pytest.mark.undestructive
# @pytest.mark.testrail_id('1665419', domain_name='AD2')
# @pytest.mark.testrail_id('1680675', domain_name='openldap2')
# @pytest.mark.ldap
# @pytest.mark.check_env_("is_ldap_plugin_installed")
# @pytest.mark.parametrize('domain_name', ['AD2', 'openldap2'])
# def test_ldap_get_group_members(os_conn, domain_name):
def test_ldap_get_group_members(domain_steps, group_steps, user_steps):

    """Test to check user list for a group

    Steps:
    1. Checks list of users for domain AD2 and group Administrators
       (similar for openldap2/group01)
    """
    # if domain_name == 'AD2':
    #     group_name = 'Administrators'
    # else:
    #     group_name = 'group01'
    domain_name = 'AD2'
    group_name = 'Administrators'
    domain = domain_steps.find_domain(name=domain_name)
    group = group_steps.find_group(name=group_name, domain=domain)
    user_steps.get_users(domain=domain)
    user_steps.get_users(domain=domain, group=group)
