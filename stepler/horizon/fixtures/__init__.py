"""
----------------
Horizon fixtures
----------------
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

from .access import *  # noqa
from .api_access import *  # noqa
from .app import *  # noqa
from .auto_use import *  # noqa
from .containers import *  # noqa
from .credentials import *  # noqa
from .defaults import *  # noqa
from .flavors import *  # noqa
from .floating_ips import *  # noqa
from .host_aggregates import *  # noqa
from .images import *  # noqa
from .instances import *  # noqa
from .keypairs import *  # noqa
from .metadata_definitions import *  # noqa
from .networks import *  # noqa
from .projects import *  # noqa
from .routers import *  # noqa
from .settings import *  # noqa
from .users import *  # noqa
from .volume_types import *  # noqa
from .volumes import *  # noqa


__all__ = sorted([  # sort for documentation
    'access_steps',
    'create_security_group',
    'security_group',

    'api_access_steps',

    'auth_steps',
    'horizon',
    'login',

    'horizon_autouse',
    'logger',
    'network_setup',
    'report_dir',
    'video_capture',
    'virtual_display',

    'create_container',
    'container',
    'containers_steps',

    'admin_only',
    'any_one',
    'user_only',

    'defaults_steps',
    'update_defaults',

    'create_flavor',
    'create_flavors',
    'flavor',
    'flavors_steps',

    'allocate_floating_ip',
    'floating_ip',
    'floating_ips_steps',

    'create_host_aggregate',
    'create_host_aggregates',
    'host_aggregate',
    'host_aggregates_steps',

    'create_image',
    'create_images',
    'images',
    'image',
    'images_steps',

    'create_instance',
    'instance',
    'instances_steps',

    'keypairs_steps_ui',
    'namespaces_steps_ui',

    'create_network',
    'create_networks',
    'network',
    'networks_steps',

    'projects_steps_ui',

    'create_router',
    'router',
    'routers_steps',

    'settings_steps',
    'update_settings',

    'create_user',
    'create_users',
    'user',
    'users_steps',

    'volume_types_steps_ui',
    'volumes_steps_ui',
])
