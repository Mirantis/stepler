"""
--------------
Horizon config
--------------
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

import os

from stepler.third_party import utils

from stepler.config import *  # noqa

UI_TIMEOUT = 30
ACTION_TIMEOUT = 60
EVENT_TIMEOUT = 180

OS_DASHBOARD_URL = os.environ.get('OS_DASHBOARD_URL')  # should be defined!
VIRTUAL_DISPLAY = os.environ.get('VIRTUAL_DISPLAY')

DEFAULT_ADMIN_NAME = 'admin'
DEFAULT_ADMIN_PASSWD = 'admin'
DEFAULT_ADMIN_PROJECT = 'admin'
ADMIN_NAME, ADMIN_PASSWD, ADMIN_PROJECT = list(
    utils.generate_ids(
        'admin', count=3))
USER_NAME, USER_PASSWD, USER_PROJECT = list(
    utils.generate_ids(
        'user', count=3))
FLOATING_NETWORK_NAME = 'admin_floating_net'
INTERNAL_NETWORK_NAME = 'admin_internal_net'

XVFB_LOCK = '/tmp/xvfb.lock'
