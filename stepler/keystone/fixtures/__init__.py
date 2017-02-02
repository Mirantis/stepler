"""
-----------------
Keystone fixtures
-----------------
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

from .domains import *  # noqa
from .ec2 import *  # noqa
from .groups import *  # noqa
from .keystone import *  # noqa
from .projects import *  # noqa
from .roles import *  # noqa
from .services import *  # noqa
from .tokens import *  # noqa
from .users import *  # noqa


__all__ = sorted([  # sort for documentation
    'create_domain',
    'domain_steps',
    'domain',

    'ec2_steps',

    'group_steps',
    'create_group',
    'group',

    'get_keystone_client',
    'keystone_client',

    'create_project',
    'get_project_steps',
    'project_steps',
    'project',
    'get_current_project',
    'current_project',

    'admin_role',
    'create_role',
    'get_role_steps',
    'role_steps',
    'role',

    'admin',
    'create_user',
    'get_user_steps',
    'user_steps',
    'user',
    'new_user_with_project',

    'token_steps',

    'get_service_steps',
    'service_steps'
])
