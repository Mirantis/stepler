"""
--------------
Logging config
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

import logging.config
import os

from stepler import config

level = logging.DEBUG if config.DEBUG else logging.INFO


config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format':
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': level,
            'formatter': 'simple',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level': logging.DEBUG,
            'class': 'logging.FileHandler',
            'filename': os.path.join(config.TEST_REPORTS_DIR, 'test.log'),
            'formatter': 'simple',
        },
    },
    'loggers': {
        'os_faults': {
            'level': logging.DEBUG,
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        '': {
            'level': logging.INFO,
            'handlers': ['console', 'file']
        },
    },
}

logging.config.dictConfig(config)
