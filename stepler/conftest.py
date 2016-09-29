"""
---------------
Global conftest
---------------

Includes fixtures available in global scope among all tests.

@author: schipiga@mirantis.com
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

from stepler.fixtures import *  # noqa
from stepler.glance.conftest import *  # noqa
from stepler.keystone.conftest import *  # noqa
from stepler.neutron.conftest import *  # noqa
from stepler.nova.conftest import *  # noqa

__all__ = [
    'admin_ssh_key_path',
    'auth_url',
    'ip_by_host',
    'session',

    'create_image',
    'create_images',
    'glance_client',
    'glance_steps',
    'ubuntu_image',
    'cirros_image',

    'create_domain',
    'domain_steps',
    'domain',
    'keystone_client',
    'create_project',
    'project_steps',
    'project',
    'admin_role',
    'create_role',
    'role_steps',
    'role',
    'admin',
    'create_user',
    'user_steps',
    'user',

    'create_network',
    'network',
    'neutron_client',
    'neutron_steps',

    'create_flavor',
    'flavor',
    'flavor_steps',
    'nova_create_floating_ip',
    'nova_floating_ip',
    'nova_floating_ip_steps',
    'create_keypair',
    'keypair',
    'keypair_steps',
    'nova_client',
    'create_security_group',
    'security_group',
    'security_group_steps',
    'create_server',
    'create_servers',
    'server',
    'server_steps',
    'ssh_proxy_data'
]

__all__.sort()

pytest_plugins = [
    'stepler.third_party.steps_checker',
    'stepler.third_party.testrail_id'
]
