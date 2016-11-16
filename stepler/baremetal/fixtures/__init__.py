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

__all__ = sorted([  # sort for documentation
    'ironic_client',

    'ironic_port_steps',
    'ironic_port',

    'ironic_node_steps',
    'create_ironic_node',
    'ironic_node',

    'ironic_chassis_steps',
    'get_ironic_chassis_steps',
    'cleanup_chassis',
    'primary_chassis',
    'unexpected_chassis_cleanup',
])
