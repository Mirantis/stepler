"""
---------------
Common fixtures
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

from .env_dependent import *  # noqa
from .openstack import *  # noqa
from .project_resources import *  # noqa
from .report import *  # noqa
from .skip import *  # noqa

__all__ = sorted([  # sort for documentation
    'admin_ssh_key_path',
    'auth_url',
    'ip_by_host',

    'get_session',
    'session',
    'os_credentials',
    'uncleanable',

    'report_log',
    'report_dir',

    'skip_test',

    'admin_project_resources',
    'create_project_resources',
])
