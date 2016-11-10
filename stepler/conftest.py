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

from stepler.baremetal.conftest import *  # noqa
from stepler.cinder.conftest import *  # noqa
from stepler.fixtures import *  # noqa
from stepler.glance.conftest import *  # noqa
from stepler.heat.conftest import *  # noqa
from stepler.keystone.conftest import *  # noqa
from stepler.neutron.conftest import *  # noqa
from stepler.nova.conftest import *  # noqa
from stepler.os_faults.conftest import *  # noqa

__all__ = sorted([  # sort for documentation
    'admin_ssh_key_path',
    'auth_url',
    'ip_by_host',
    'get_session',
    'session',
    'uncleanable',
    'report_log',
    'report_dir',

    'volume',
    'cinder_client',
    'get_cinder_client',
    'get_transfer_steps',
    'get_volume_steps',
    'volume_steps',
    'volume_type_steps',
    'volume_type',
    'create_volume_type',
    'cinder_quota_steps',
    'snapshot_steps',
    'snapshot',
    'snapshots_cleanup',
    'transfer_steps',
    'big_snapshot_quota',
    'create_volume_transfer',
    'create_backup',
    'backup_steps',

    'heat_client',
    'stack_steps',
    'create_stack',
    'empty_stack',
    'read_heat_template',
    'heat_resource_steps',
    'heat_resource_type_steps',
    'get_template_path',

    'api_glance_client_v1',
    'api_glance_client_v2',
    'get_glance_client',
    'glance_client_v1',
    'glance_client_v2',
    'api_glance_steps',
    'api_glance_steps_v1',
    'api_glance_steps_v2',
    'cirros_image',
    'get_glance_steps',
    'glance_steps',
    'glance_steps_v1',
    'glance_steps_v2',
    'ubuntu_image',
    'ubuntu_xenial_image',

    'create_group',
    'create_domain',
    'domain_steps',
    'domain',
    'group_steps',
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
    'new_user_with_project',

    'create_network',
    'network',
    'public_network',
    'internal_network',
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
    'get_neutron_client',
    'get_network_steps',
    'get_router_steps',
    'get_subnet_steps',
    'admin_internal_network',
    'baremetal_network',

    'create_flavor',
    'flavor',
    'flavor_steps',
    'tiny_flavor',

    'nova_create_floating_ip',
    'nova_floating_ip',
    'nova_floating_ip_steps',
    'host_steps',
    'hypervisor_steps',
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
    'create_server_context',
    'create_servers_context',
    'server',
    'server_steps',
    'get_ssh_proxy_cmd',
    'disable_nova_config_drive',
    'live_migration_server',
    'generate_traffic',

    'get_availability_zone_steps',
    'availability_zone_steps',
    'nova_availability_zone',
    'nova_availability_zone_hosts',

    'os_faults_client',
    'os_faults_steps',
    'patch_ini_file_and_restart_services',
    'execute_command_with_rollback',
    'nova_api_node',

    'create_ironic_node',
    'ironic_node',
    'ironic_node_steps',
    'ironic_port',
    'ironic_port_steps',
])

_plugins = [
    'bugs_file',
    'destructive_dispatcher',
    'idempotent_id',
    'reports_cleaner',
    'steps_checker',
]

pytest_plugins = map(lambda plugin: 'stepler.third_party.' + plugin, _plugins)
