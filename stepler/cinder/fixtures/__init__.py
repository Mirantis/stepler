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
from .volume_types import *  # noqa
from .volumes import *  # noqa

__all__ = sorted([  # sort for documentation
    'get_backup_steps',
    'backup_steps',
    'create_backup',
    'cleanup_backups',

    'cinder_client',
    'get_cinder_client',

    'get_cinder_quota_steps',
    'cinder_quota_steps',
    'big_snapshot_quota',
    'volume_size_quota',

    'get_snapshot_steps',
    'snapshot_steps',
    'cleanup_snapshots',
    'volume_snapshot',

    'transfer_steps',
    'create_volume_transfer',
    'get_transfer_steps',
    'cleanup_transfers',

    'volume_type_steps',
    'create_volume_type',
    'volume_type',

    'cleanup_volumes',
    'get_volume_steps',
    'primary_volumes',
    'unexpected_volumes_cleanup',
    'upload_volume_to_image',
    'volume',
    'bootable_volume',
    'volumes',
    'volume_steps',
])
