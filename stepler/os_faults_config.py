"""
----------------
Os-faults config
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

import os

# Configure with file
OS_FAULTS_CONFIG = os.environ.get('OS_FAULTS_CONFIG')


def getenv(suffix, default=None):
    return os.environ.get("OS_FAULTS_{}".format(suffix), default)


# Configure with shell environment variables if no file passed
OS_FAULTS_DICT_CONFIG = {
    'cloud_management': {
        'driver': getenv('CLOUD_DRIVER', 'devstack'),
        'args': {
            'address': getenv('CLOUD_DRIVER_ADDRESS', 'devstack.local'),
            'username': getenv('CLOUD_DRIVER_USERNAME', 'root'),
            'private_key_file': getenv('CLOUD_DRIVER_KEYFILE')
        }
    },
    'power_management': {
        'driver': getenv('POWER_DRIVER', 'libvirt'),
        'args': {
            'connection_uri': getenv('POWER_DRIVER_URI',
                                     'qemu+unix:///system'),
        }
    }
}
