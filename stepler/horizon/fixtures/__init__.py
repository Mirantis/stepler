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
from .overview import *  # noqa
from .projects import *  # noqa
from .routers import *  # noqa
from .security_groups import *  # noqa
from .settings import *  # noqa
from .users import *  # noqa
from .volume_types import *  # noqa
from .volumes import *  # noqa


__all__ = sorted([  # sort for documentation
    'security_groups_steps_ui',
    'horizon_create_security_group',
    'horizon_security_group',

    'api_access_steps_ui',

    'auth_steps',
    'horizon',
    'login',

    'horizon_autouse',
    'logger',
    'network_setup',
    'report_dir',
    'video_capture',
    'virtual_display',

    'create_container_ui',
    'containers_steps_ui',
    'container',

    'admin_only',
    'any_one',
    'user_only',

    'defaults_steps_ui',
    'update_defaults',

    'flavors_steps_ui',

    'allocate_floating_ip',
    'floating_ip',
    'floating_ips_steps_ui',

    'host_aggregates_steps_ui',

    'horizon_images',
    'horizon_image',
    'images_steps_ui',

    'instances_steps_ui',
    'horizon_servers',
    'horizon_servers_with_private_image',
    'horizon_server',
    'horizon_server_with_private_image',

    'keypairs_steps_ui',
    'namespaces_steps_ui',

    'networks_steps_ui',

    'overview_steps_ui',

    'projects_steps_ui',
    'project_name_non_ascii',

    'routers_steps_ui',

    'settings_steps_ui',
    'update_settings',

    'users_steps_ui',
    'new_user_login',

    'volume_types_steps_ui',
    'volumes_steps_ui',
])
