"""
------------
NFV fixtures
------------
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

from .nfv import *  # noqa


__all__ = sorted([  # sort for documentation
    'nfv_steps',
    'computes_without_hp',
    'computes_with_hp_2mb',
    'computes_with_hp_1gb',
    'computes_with_hp_mixed',
    'create_servers_to_allocate_hp',
])
