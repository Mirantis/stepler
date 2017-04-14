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
from stepler.object_storage.conftest import *  # noqa
from stepler.os_faults.conftest import *  # noqa

__all__ = sorted([  # sort for documentation
    'get_role_steps',
    'get_user_steps',
    'get_keystone_client',
    'predicates',
    'get_project_steps',
    'admin_ssh_key_path',
    'auth_url',
    'ip_by_host',
    'get_session',
    'session',
    'skip_test',
    'credentials',
    'create_user_with_project',
    'admin_project_resources',
    'uncleanable',
    'report_log',
    'report_dir',

    'get_backup_steps',
    'backup_steps',
    'create_backup',
    'cleanup_backups',
    'cinder_client',
    'get_cinder_client',
    'cinder_quota_steps',
    'big_snapshot_quota',
    'volume_size_quota',
    'get_snapshot_steps',
    'snapshot_steps',
    'cleanup_snapshots',
    'volume_snapshot',
    'transfer_steps',
    'create_volume_transfer',
    'get_transfer_steps',
    'cleanup_transfers',
    'volume_type_steps',
    'create_volume_type',
    'volume_type',
    'cleanup_volumes',
    'get_volume_steps',
    'primary_volumes',
    'unexpected_volumes_cleanup',
    'upload_volume_to_image',
    'volume',
    'bootable_volume',
    'volumes',
    'volume_steps',

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
    'create_images_context',
    'get_glance_steps',
    'glance_steps',
    'glance_steps_v1',
    'glance_steps_v2',
    'ubuntu_image',
    'ubuntu_xenial_image',
    'conntrack_cirros_image',

    'create_group',
    'create_domain',
    'domain_steps',
    'domain',
    'group_steps',
    'keystone_client',
    'create_project',
    'project_steps',
    'project',
    'current_project',
    'admin_role',
    'create_role',
    'role_steps',
    'role',
    'admin',
    'create_user',
    'user_steps',
    'user',
    'new_user_with_project',
    'ec2_steps',

    'create_network',
    'network',
    'public_network',
    'create_port',
    'port',
    'create_subnet',
    'subnet',
    'create_router',
    'router',
    'routers_cleanup',
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
    'baremetal_network',
    'net_subnet_router',
    'agent_steps',
    'neutron_create_security_group',
    'neutron_security_group',

    'create_flavor',
    'flavor',
    'flavor_steps',
    'tiny_flavor',
    'small_flavor',
    'baremetal_flavor',

    'nova_limit_steps',
    'nova_absolute_limits',

    'nova_floating_ip',
    'nova_floating_ip_steps',
    'host_steps',
    'hypervisor_steps',
    'keypair',
    'keypair_steps',
    'nova_client',
    'get_nova_client',
    'generate_os_workload',
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
    'get_security_group_steps',
    'ubuntu_server',
    'servers_to_evacuate',

    'get_availability_zone_steps',
    'availability_zone_steps',
    'nova_availability_zone',
    'nova_availability_zone_hosts',
    'nova_service_steps',

    'os_faults_client',
    'os_faults_steps',
    'patch_ini_file_and_restart_services',
    'execute_command_with_rollback',
    'nova_api_node',
    'ironic_api_node',
    'shutdown_nodes',

    'get_ironic_node_steps',
    'unexpected_node_cleanup',
    'ironic_node_steps',
    'cleanup_nodes',
    'primary_nodes',
    'ironic_node',
    'get_ironic_port_steps',
    'ironic_port',
    'ironic_port_steps',
    'ironic_chassis_steps',
    'get_ironic_chassis_steps',
    'cleanup_chassis',
    'primary_chassis',
    'unexpected_chassis_cleanup',

    'api_ironic_client_v1',
    'get_ironic_client',
    'ironic_client_v1',
    'get_api_ironic_client',
    'get_api_ironic_steps',
    'ironic_steps_v1',
    'api_ironic_steps_v1',
    'api_ironic_steps',

    'container_steps',
    's3_client',
    'swift_client',
])

_plugins = [
    'bugs_file',
    'default_project',
    'destructive_dispatcher',
    'idempotent_id',
    'no_tests_found',
    'reports_cleaner',
    'steps_checker',
    'supported_platforms',
]

pytest_plugins = map(lambda plugin: 'stepler.third_party.' + plugin, _plugins)
