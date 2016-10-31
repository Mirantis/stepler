"""
---------------
Cinder fixtures
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

from .backups import *  # noqa
from .cinder import *  # noqa
from .quota import *  # noqa
from .snapshots import *  # noqa
from .transfers import *  # noqa
from .volumes import *  # noqa
from .volume_types import *  # noqa

__all__ = sorted([  # sort for documentation
    'create_volume',
    'create_volumes',
    'cinder_client',
    'get_cinder_client',
    'get_volume_steps',
    'volume_steps',
    'volume_type_steps',
    'volume_type',
    'create_volume_type',
    'upload_volume_to_image',
    'volume',
    'volumes_cleanup',

    'cinder_quota_steps',

    'transfer_steps',
    'create_volume_transfer',

    'snapshot_steps',
    'create_snapshot',
    'create_snapshots',
    'volume_snapshot',

    'create_backup',
    'backup_steps',
])
