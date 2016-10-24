"""
---------------
Global conftest
---------------

Includes fixtures available in global scope among all tests.
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
from stepler.cinder.conftest import *  # noqa
from stepler.heat.conftest import *  # noqa
from stepler.glance.conftest import *  # noqa
from stepler.keystone.conftest import *  # noqa
from stepler.neutron.conftest import *  # noqa
from stepler.nova.conftest import *  # noqa
from stepler.os_faults.conftest import *  # noqa

__all__ = sorted([  # sort for documentation
    'admin_ssh_key_path',
    'auth_url',
    'ip_by_host',
    'session',
    'report_log',
    'report_dir',

    'create_volume',
    'create_volumes',
    'cinder_client',
    'volume_steps',

    'heat_client',
    'resource_steps',
    'stack_steps',
    'create_stack',
    'read_heat_template',

    'api_glance_client_v1',
    'api_glance_client_v2',
    'get_glance_client',
    'glance_client_v1',
    'glance_client_v2',
    'api_glance_steps',
    'api_glance_steps_v1',
    'api_glance_steps_v2',
    'cirros_image',
    'create_image',
    'create_images',
    'get_glance_steps',
    'glance_steps',
    'glance_steps_v1',
    'glance_steps_v2',
    'ubuntu_image',
    'ubuntu_xenial_image',

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
    'public_network',
    'create_port',
    'port',
    'create_subnet',
    'subnet',
    'create_router',
    'router',
    'add_router_interfaces',
    'create_port',
    'neutron_client',
    'network_steps',
    'router_steps',
    'subnet_steps',
    'port_steps',

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
    'nova_volume_steps',
    'attach_volume_to_server',
    'detach_volume_from_server',
    'create_server',
    'create_server_context',
    'create_servers',
    'create_servers_context',
    'server',
    'server_steps',
    'get_ssh_proxy_cmd',

    'os_faults_client',
    'os_faults_steps',
    'patch_ini_file_and_restart_services',
])

pytest_plugins = [
    'stepler.third_party.reports_cleaner',
    'stepler.third_party.steps_checker',
    'stepler.third_party.destructive_dispatcher',
    'stepler.third_party.idempotent_id',
]
