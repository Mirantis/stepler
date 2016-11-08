"""
-------------------
CLI client fixtures
-------------------
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

from .baremetal import *  # noqa
from .base import *  # noqa
from .cinder import *  # noqa
from .glance import *  # noqa
from .heat import *  # noqa
from .nova import *  # noqa
from .openstack import *  # noqa

__all__ = [
    'remote_executor',

    'cli_cinder_steps',

    'cli_glance_steps',
    'cli_download_image',

    'cli_heat_steps',
    'empty_heat_template_path',

    'cli_ironic_steps',

    'cli_nova_steps',
    'cli_openstack_steps',
]
