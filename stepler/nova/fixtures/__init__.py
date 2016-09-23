"""
Nova fixtures package.

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

from .flavors import *  # noqa
from .floating_ips import *  # noqa
from .keypairs import *  # noqa
from .nova import *  # noqa
from .servers import *  # noqa
from .security_groups import *  # noqa

__all__ = [
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
