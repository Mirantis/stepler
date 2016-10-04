"""
-------------------
Keystone LDAP tests
-------------------
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

from stepler.keystone.config import (LDAP_DOMAIN_NAMES,
                                     LDAP_DOMAIN_GROUPS)  # noqa


def test_ldap_basic_functions(domain_steps, group_steps, user_steps):
    """**Scenario:** Check basic functionality (get users, groups)

    **Setup:**

    **Steps:**

        #. Find LDAP domains
        #. For each domain, checks lists of users and groups

    **Teardown:**

    """
    for domain_name in LDAP_DOMAIN_NAMES:
        domain = domain_steps.get_domain(name=domain_name)
        group_steps.get_groups(domain=domain)
        user_steps.get_users(domain=domain)


def test_ldap_get_group_members(domain_steps, group_steps, user_steps):
    """**Scenario:** Check user list for groups of LDAP domains

    **Setup:**

    **Steps:**

        #. Checks list of users for groups of LDAP domains

    **Teardown:**

    """
    for domain_name in LDAP_DOMAIN_GROUPS:
        domain = domain_steps.get_domain(name=domain_name)
        group_name = LDAP_DOMAIN_GROUPS[domain_name]
        group = group_steps.get_group(name=group_name, domain=domain)
        user_steps.get_users(domain=domain, group=group)
