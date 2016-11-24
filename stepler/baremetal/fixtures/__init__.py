"""
---------------
Ironic fixtures
---------------
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

from .chassis import *  # noqa
from .node import *  # noqa
from .port import *  # noqa
from .ironic import *  # noqa
from .clients import *  # noqa
from .api_node_steps import *  # noqa

__all__ = sorted([  # sort for documentation
    'ironic_client',
    'get_ironic_client',

    'get_ironic_port_steps',
    'ironic_port_steps',
    'ironic_port',

    'get_ironic_node_steps',
    'unexpected_node_cleanup',
    'ironic_node_steps',
    'cleanup_nodes',
    'primary_nodes',
    'ironic_node',

    'ironic_chassis_steps',
    'get_ironic_chassis_steps',
    'cleanup_chassis',
    'primary_chassis',
    'unexpected_chassis_cleanup',

    'api_ironic_client_v1',
    'get_api_ironic_client',
    'ironic_client_v1',
    'get_api_ironic_steps',
    'ironic_steps_v1',
    'api_ironic_steps_v1',
    'api_ironic_steps',
])
