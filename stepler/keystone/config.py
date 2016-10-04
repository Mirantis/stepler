"""
---------------------
Keystone tests config
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
