"""
-------------
Nova fixtures
-------------
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

from .availability_zones import *  # noqa
from .flavors import *  # noqa
from .floating_ips import *  # noqa
from .hosts import *  # noqa
from .hypervisor import *  # noqa
from .keypairs import *  # noqa
from .network_workload import *  # noqa
from .nova import *  # noqa
from .nova_volumes import *  # noqa
from .security_groups import *  # noqa
from .servers import *  # noqa


__all__ = sorted([  # sort for documentation
    'get_availability_zone_steps',
    'availability_zone_steps',
    'nova_availability_zone',
    'nova_availability_zone_hosts',

    'create_flavor',
    'flavor',
    'flavor_steps',
    'tiny_flavor',
    'baremetal_flavor',
    'public_flavor',

    'nova_create_floating_ip',
    'nova_floating_ip',
    'nova_floating_ip_steps',

    'host_steps',

    'hypervisor_steps',
    'sorted_hypervisors',

    'keypair',
    'keypair_steps',
    'keypairs_cleanup',

    'get_nova_client',
    'nova_client',
    'disable_nova_config_drive',
    'skip_live_migration_tests',
    'unlimited_live_migrations',
    'nova_ceph_enabled',
    'disable_nova_use_cow_images',
    'big_nova_reclaim_instance_interval',
    'small_nova_reclaim_instance_interval',

    'create_security_group',
    'security_group',
    'security_group_steps',
    'get_security_group_steps',

    'nova_volume_steps',
    'attach_volume_to_server',
    'detach_volume_from_server',

    'create_server_context',
    'create_servers_context',
    'evacuated_servers',
    'get_server_steps',
    'get_ssh_proxy_cmd',
    'server',
    'server_steps',
    'live_migration_server',
    'live_migration_servers',
    'live_migration_servers_with_volumes',
    'servers_cleanup',
    'generate_traffic',
    'ubuntu_server',
    'unexpected_servers_cleanup',
])
