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
from .hypervisor import *  # noqa
from .keypairs import *  # noqa
from .nova import *  # noqa
from .servers import *  # noqa
from .nova_volumes import *  # noqa
from .security_groups import *  # noqa

__all__ = sorted([  # sort for documentation
    'get_availability_zone_steps',
    'availability_zone_steps',
    'nova_availability_zone',
    'nova_availability_zone_hosts',

    'create_flavor',
    'flavor',
    'flavor_steps',
    'tiny_flavor',

    'nova_create_floating_ip',
    'nova_floating_ip',
    'nova_floating_ip_steps',

    'hypervisor_steps',

    'create_keypair',
    'keypair',
    'keypair_steps',

    'get_nova_client',
    'nova_client',
    'disable_nova_config_drive',

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
    'get_server_steps',
    'get_ssh_proxy_cmd',
    'server',
    'server_steps',
    'servers_cleanup',

])
